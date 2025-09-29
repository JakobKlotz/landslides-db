import json
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from sqlalchemy.dialects.postgresql import insert

from src.constants import AUSTRIA, TARGET_CRS
from src.duplicates import is_duplicated
from src.models import Landslides
from src.utils import create_db_session, create_source_from_metadata, dump_gpkg


class GlobalFatalLandslides:
    def __init__(self, *, file_path: str | Path, metadata_file: str | Path):
        # Ensure that points are within Austria
        # CRS mis-match between the two files is handled internally by
        # geopandas
        self.data = gpd.read_file(file_path, mask=AUSTRIA)

        with Path(metadata_file).open() as f:
            self.metadata = json.load(f)

    def subset(self):
        """Subset the data"""
        self.data = self.data.query("Country == 'Austria'")
        # Merge trigger, report and source into description
        self.data["description"] = (
            "Report: "
            + self.data["Report_1"]
            + "; Trigger: "
            + self.data["Trigger"]
            + "; Source: "
            + self.data["Source_1"]
        ).str.replace("\n", " ")  # remove unnecessary newlines
        # Drop unused columns
        self.data = self.data[["Date", "description", "geometry"]]
        self.data = self.data.sort_values("Date").reset_index(drop=True)

    def clean(self):
        """Clean the data."""
        # Manually assign type (landslide, rockfall)
        warnings.warn(
            message="Caution: Types are assigned to the data."
            "If you have changed the source data of the global fatal landslide"
            " database check the results",
            stacklevel=2,
        )

        # Remove Z coordinate from points
        self.data["geometry"] = self.data["geometry"].force_2d()
        # Project to TARGET_CRS
        self.data = self.data.to_crs(crs=TARGET_CRS)

        # Combination of date & geometry is unique
        # Those two events were rockfalls, see their description
        rockfall_events = gpd.GeoDataFrame(
            data={
                "Date": pd.to_datetime(
                    ["2005-08-23 00:00:00", "2008-03-01 00:00:00"]
                ),
                "geometry": [
                    Point(651192.3868625985, 5212271.343543028),
                    Point(807247.7813673844, 5256032.494610518),
                ],
                "type_override": ["rockfall", "rockfall"],
            },
            crs=self.data.crs,
        )

        # Perform a spatial join (to account for slight floating point
        # differences in the geometries)
        self.data = gpd.sjoin_nearest(
            self.data,
            rockfall_events,
            how="left",
            max_distance=1,
        )
        # A spatial match is only valid if the dates also match.
        # Invalidate matches where the dates are different.
        date_mismatch = self.data["Date_left"] != self.data["Date_right"]
        self.data.loc[date_mismatch, "type_override"] = None

        # Default event is mapped to "mass movement (undefined type)" stemming
        # from the GeoSphere data set
        self.data["type"] = self.data["type_override"].fillna(
            "mass movement (undefined type)"
        )
        # Drop helper columns from the join
        self.data = self.data.drop(
            columns=["type_override", "index_right", "Date_right"]
        ).rename(columns={"Date_left": "date"})

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
                landslide_date=row["date"].date(),
                landslide_geom=row["geom_wkt"],
            ),
            axis=1,
        )

        n_duplicates = data_to_import["duplicated"].sum()
        if n_duplicates > 0:
            warnings.warn(
                message=f"Found {n_duplicates} duplicate/s "
                "in the Global Fatal Landslide data.",
                stacklevel=2,
            )

        if file_dump:
            dump_gpkg(data_to_import, output_file=file_dump)

        # Import events, remove all duplicates first
        data_to_import = data_to_import[~data_to_import["duplicated"]]

        # must be a list of dicts for the insert statement
        landslide_records = data_to_import.apply(
            lambda row: {
                "type": row["type"],
                "date": row["date"].date(),
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
                "Global Fatal Landslide records."
            )
        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")
        finally:
            session.close()

    def run(self, file_dump: str | None = None):
        """Run all processing steps."""
        self.subset()
        self.clean()
        self.import_to_db(file_dump=file_dump)
