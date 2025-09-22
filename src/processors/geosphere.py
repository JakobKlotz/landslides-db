import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import settings
from src.constants import TARGET_CRS
from src.models import Landslides, Sources


class GeoSphere:
    def __init__(self, *, file_path: str | Path, metadata_file: str | Path):
        self.data = gpd.read_file(file_path)

        with Path(metadata_file).open() as f:
            self.metadata = json.load(f)

    def _check_geom(self):
        """Check if geometries are given."""
        if any(self.data.geometry.isna()):
            raise ValueError("Some geometries are null.")

    def subset(self):
        """Subset the data to only include necessary columns."""
        necessary_columns = [
            "inspireId_localId",
            "validFrom",
            "description",
            "geometry",
        ]
        # all other columns have no real meaning, often unpopulated or
        # a constant
        self.data = self.data[necessary_columns]

    def clean(self):
        """Clean the data."""
        # validFrom to date (coerce - historical dates are in there)
        self.data["validFrom"] = pd.to_datetime(
            self.data["validFrom"], errors="coerce"
        ).dt.date

        def _remove_duplicates(self):
            self.data = self.data.sort_values(by="validFrom", ascending=False)
            # remove all *obvious* duplicates, keep most recent entry
            self.data = self.data.drop_duplicates(
                subset=["validFrom", "description", "geometry"], keep="last"
            )
            # remove entries with no valid date (validFrom) among the
            # duplicates
            dup = self.data[
                # get all duplicates (keep=False)
                self.data.duplicated(subset="geometry", keep=False)
            ].sort_values(by=["geometry", "validFrom"])
            # remove all entries with no validFrom date *among the duplicates*
            ids_to_drop = dup[dup["validFrom"].isna()]["inspireId_localId"]
            # drop them from the original data set
            self.data = self.data[
                ~self.data["inspireId_localId"].isin(ids_to_drop)
            ]

        _remove_duplicates(self)

    def flag(self, days: int = 1):
        """Flag potential duplicates based on a time gap (in days),
        same geometry and description."""
        dup = self.data[
            self.data.duplicated(subset="geometry", keep=False)
        ].sort_values(by=["geometry", "validFrom"])
        # need a datetime
        dup["validFrom"] = pd.to_datetime(dup["validFrom"])
        # Calculate the time difference in days to the previous entry within
        # the same geometry group
        dup["time_diff_days"] = (
            # use to_wkt(), else groupby fails
            dup.groupby(dup.geometry.to_wkt())["validFrom"].diff()
        ).dt.days

        # Check if the description is the same as the previous entry
        # in the group
        dup["same_description"] = dup.groupby(dup.geometry.to_wkt())[
            "description"
        ].transform(lambda x: x.eq(x.shift()))

        # Flag potential errors if the time gap is small (e.g., <= 1 day)
        # and description is the same
        dup["is_likely_error"] = (dup["time_diff_days"] <= days) & (
            dup["same_description"]
        )
        print(
            f"Found {dup['is_likely_error'].sum()} "
            f"likely duplicates with a {days}-day threshold. Flagged them."
        )
        # map results back to original data
        self.data = self.data.merge(
            dup[["inspireId_localId", "is_likely_error"]],
            on="inspireId_localId",
            how="left",
        )
        # use mask() instead of fillna() to avoid upcasting warning
        # convert NaN to False
        self.data["is_likely_error"] = self.data["is_likely_error"].mask(
            self.data["is_likely_error"].isna(), False
        )
        self.data["is_likely_error"] = self.data["is_likely_error"].astype(
            bool
        )

    def reproject(self, crs: str = TARGET_CRS):
        """Reproject the data to the target CRS."""
        self.data = self.data.to_crs(crs=crs)

    def dump(self, out_path: str | Path, overwrite: bool = True):
        """Dump the processed data to a file."""
        if Path(out_path).exists() and not overwrite:
            raise FileExistsError(
                f"File {out_path} already exists. Skipping dump. "
                f"Set overwrite=True to overwrite."
            )
        # delete an existing GeoPackage, overwriting leads to issues
        Path(out_path).unlink(missing_ok=True)
        self.data.to_file(out_path, driver="GPKG")

    def import_to_db(self):
        """Import the data into a PostGIS database."""

        def _create_session():
            engine = create_engine(
                settings.DB_URI, echo=False, plugins=["geoalchemy2"]
            )
            return sessionmaker(bind=engine)

        Session = _create_session()  # noqa: N806
        session = Session()

        # add source entry
        source = Sources(
            name=self.metadata["name"],
            downloaded=pd.to_datetime(self.metadata["downloaded"]).date(),
            modified=pd.to_datetime(self.metadata["modified"]).date(),
            license=self.metadata["license"],
            url=self.metadata["url"],
        )

        # TODO verify if that's the most sensible option
        data_to_import = self.data[~self.data["is_likely_error"]].copy()
        # see https://geoalchemy-2.readthedocs.io/en/latest/orm_tutorial.html#create-an-instance-of-the-mapped-class
        data_to_import["geom_wkt"] = (
            f"SRID={TARGET_CRS};" + data_to_import["geometry"].to_wkt()
        )
        landslides = data_to_import.apply(
            lambda row: Landslides(
                date=row["validFrom"] if pd.notna(row["validFrom"]) else None,
                description=row["description"],
                geom=row["geom_wkt"],
                source=source,
            ),
            axis=1,
        )

        try:
            session.add_all(landslides)
            session.commit()
            print(f"Successfully imported {len(landslides)} records.")
        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")
        finally:
            session.close()

    def run(self, file_dump: str | None = None):
        """Run all processing steps."""
        self._check_geom()
        self.subset()
        self.clean()
        self.flag()
        self.reproject()

        if file_dump:
            self.dump(file_dump)
        print("Processing complete.")

        self.import_to_db()
