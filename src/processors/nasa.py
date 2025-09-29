import json
import warnings
from pathlib import Path

import geopandas as gpd
from sqlalchemy.dialects.postgresql import insert

from constants import AUSTRIA
from src.constants import TARGET_CRS
from src.duplicates import is_duplicated
from src.models import Landslides
from src.utils import create_db_session, create_source_from_metadata, dump_gpkg


class Nasa:
    """Import NASA COOLR landslide report points."""

    def __init__(self, *, file_path: str | Path, metadata_file: str | Path):
        # Ensure that points are within Austria
        # CRS mis-match between the two files is handled internally by
        # geopandas
        self.data = gpd.read_file(file_path, mask=AUSTRIA)
        # sanity check
        if not len(self.data) == (self.data["country_na"] == "Austria").sum():
            raise ValueError("Some points are not in Austria")

        with Path(metadata_file).open() as f:
            self.metadata = json.load(f)

    def clean(self):
        """Subset the data"""
        # Date must be given
        self.data = self.data[~self.data["event_date"].isna()]
        # To comply with the license, keep source_nam and source_lin and add
        # them to description
        self.data["description"] = (
            "Report: "
            + self.data["event_desc"]
            + "; Source Link: "
            + self.data["source_lin"]
            + "; Source Name: "
            + self.data["source_nam"]
        ).str.replace("\n", " ")  # remove newlines

        columns_to_keep = [
            "description",
            "event_date",
            "landslide_",
            "geometry",
        ]
        self.data = self.data[columns_to_keep]

        # Map categories; GeoSphere types are used as basis:
        # ['gravity slide or flow' 'mass movement (undefined type)' 'rockfall'
        # 'collapse, sinkhole' 'deep seated rock slope deformation']
        type_mapping = {
            # term landslide is very general and doesn't specify any type
            # of movement -> mass movement
            "landslide": "mass movement (undefined type)",
            "mudslide": "gravity slide or flow",
            "rock_fall": "rockfall",
            "topple": "rockfall",
            "debris_flow": "gravity slide or flow",
            # is dropped
            "snow_avalanche": None,
        }

        types = []
        for cat in self.data["landslide_"]:
            try:
                types.append(type_mapping[cat])
            except KeyError as err:
                raise UserWarning(
                    f"New category {cat} encountered!\nCheck the type mapping"
                ) from err
        self.data["type"] = types

        # Remove all events with no type
        self.data = self.data[~self.data["type"].isna()]
        self.data["event_date"] = self.data["event_date"].date()

    def import_to_db(self, file_dump: str | None = None):
        """Import to PostGIS database."""
        Session = create_db_session()  # noqa: N806
        session = Session()

        source = create_source_from_metadata(self.metadata)
        # The source object needs to be added to the session to get an ID
        # before we can reference it.
        session.add(source)
        session.flush()

        data_to_import = self.data.copy()
        # see https://geoalchemy-2.readthedocs.io/en/latest/orm_tutorial.html#create-an-instance-of-the-mapped-class
        data_to_import["geom_wkt"] = (
            f"SRID={TARGET_CRS};" + data_to_import["geometry"].to_wkt()
        )
        # Check all events, and flag potential duplicates
        data_to_import["duplicated"] = data_to_import.apply(
            lambda row: is_duplicated(
                session=session,
                landslide_date=row["date"],
                landslide_geom=row["geom_wkt"],
            ),
            axis=1,
        )

        n_duplicates = data_to_import["duplicated"].sum()
        if n_duplicates > 0:
            warnings.warn(
                message=f"Found {n_duplicates} duplicate/s", stacklevel=2
            )

        if file_dump:
            dump_gpkg(data_to_import, output_file=file_dump)

        # Import events, remove all duplicates first
        data_to_import = data_to_import[~data_to_import["duplicated"]]

        # must be a list of dicts for the insert statement
        landslide_records = data_to_import.apply(
            lambda row: {
                "type": row["type"],
                "date": row["event_date"],
                "description": row["description"],
                "geom": row["geom_wkt"],
                "source_id": source.id,
            },
            axis=1,
        ).tolist()

        stmt = insert(Landslides).values(landslide_records)

        try:
            session.execute(stmt)
            session.commit()
            print(
                f"Successfully imported {len(data_to_import)} "
                "NASA COOLR events."
            )
        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")
        finally:
            session.close()
