import os
from pathlib import Path

import geopandas as gpd
import pandas as pd
from constants import TARGET_CRS
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from scripts.models import Landslides


class GeoSphere:
    def __init__(self, file_path: str | Path):
        self.data = gpd.read_file(file_path)

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

    def _clean(self):
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

    def _flag(self, days: int = 1):
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

    def reproject(self, crs: str = TARGET_CRS):
        """Reproject the data to the target CRS."""
        self.data = self.data.to_crs(crs=crs)

    def dump(self, out_path: str | Path):
        """Dump the processed data to a file."""
        self.data.to_file(out_path, driver="GPKG")

    def import_to_db(self):
        """Import the data into a PostGIS database."""

        def _create_session():
            load_dotenv()
            db_user, db_password = (
                os.getenv("DB_USER"),
                os.getenv("DB_PASSWORD"),
            )
            db_host, db_name = os.getenv("DB_HOST"), os.getenv("DB_NAME")
            db_uri = (
                f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
            )

            engine = create_engine(db_uri, echo=True, plugins=["geoalchemy2"])
            return sessionmaker(bind=engine)

        session = _create_session()

        # remove rows with likely errors
        data_to_import = self.data[~self.data["is_likely_error"]]
        data_to_import["geom_wkt"] = data_to_import.geometry.apply(
            lambda geom: f"SRID={TARGET_CRS};{geom.wkt}"
        )

        records = data_to_import.apply(
            lambda row: Landslides(
                date=row["validFrom"],
                description=row["description"],
                geom=row["geom_wkt"],
            ),
            axis=1,
        )
        try:
            session.add_all(records)
            session.commit()
            print(f"Successfully imported {len(records)} records.")
        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")
        finally:
            session.close()

    def run(self, file_dump: str | None = None):
        """Run all processing steps."""
        self._check_geom()
        self.subset()
        self._clean()
        self._flag()
        self.reproject()

        if file_dump:
            self.dump(file_dump)
        print("Processing complete.")

        self.import_to_db()
