from pathlib import Path

import geopandas as gpd
import pandas as pd

from db.models import Classification
from db.processors.base import BaseProcessor
from db.utils import create_db_session


class GeoSphere(BaseProcessor):
    """GeoSphere Austria data."""

    def __init__(self, *, file_path: str | Path):
        super().__init__(file_path=file_path, dataset_name="GeoSphere")

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
        # description is a classification
        # (rockfall, gravity slide or flow, ...)
        self.data = self.data.rename(columns={"description": "classification"})

    def clean(self):
        """Clean the data."""
        # validFrom to date (coerce - historical dates are in there)
        self.data["validFrom"] = pd.to_datetime(
            self.data["validFrom"], errors="coerce"
        ).dt.date
        # Remove all entries with no date
        self.data = self.data[~self.data["validFrom"].isna()]

        self.data = self.data.sort_values(by="validFrom", ascending=False)
        # remove all *obvious* duplicates, keep most recent entry
        self.data = self.data.drop_duplicates(
            subset=["validFrom", "classification", "geometry"], keep="last"
        )

    def flag(self, days: int = 1):
        """Flag potential duplicates based on a time gap (in days),
        exact same geometry and classification."""
        dup = self.data[
            self.data.duplicated(subset="geometry", keep=False)  # get all dups
        ].sort_values(by=["geometry", "validFrom"])
        # need a datetime
        dup["validFrom"] = pd.to_datetime(dup["validFrom"])
        # Calculate the time difference in days to the previous entry within
        # the same geometry group
        dup["time_diff_days"] = (
            # use to_wkt(), else groupby fails
            dup.groupby(dup.geometry.to_wkt())["validFrom"].diff()
        ).dt.days

        # Check if the classification is the same as the previous entry
        # in the group
        dup["same_classification"] = dup.groupby(dup.geometry.to_wkt())[
            "classification"
        ].transform(lambda x: x.eq(x.shift()))

        # Flag potential errors if the time gap is small (e.g., <= 1 day)
        # and classification is the same
        dup["is_likely_error"] = (dup["time_diff_days"] <= days) & (
            dup["same_classification"]
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

    def reproject(self):
        """Reproject the data to the target CRS."""
        self.data = self.data.to_crs(crs=self.target_crs)

    def populate_classification_table(self):
        """Populate the classification table with unique landslide
        classifications."""
        Session = create_db_session()  # noqa: N806
        with Session() as session:
            unique_classifications = set(
                sorted(self.data["classification"].unique())
            )

            if not unique_classifications:
                raise RuntimeError("No classifications found!")

            new_classifications = [
                Classification(name=classification)
                for classification in unique_classifications
            ]
            session.add_all(new_classifications)
            session.commit()
            print(f"Added {len(unique_classifications)} classifications.")

    def import_to_db(self, file_dump: str | None = None):
        """Import the data into a PostGIS database."""
        # For GeoSphere, we only remove likely errors, not check for duplicates
        # against the DB as it's considered our base dataset.
        data_to_import = self.data[~self.data["is_likely_error"]].copy()

        column_map = {
            "classification": "classification",
            "date": "validFrom",
            # report fields are None (no appropriate field)
        }
        self._import_to_db(
            data_to_import=data_to_import,
            column_map=column_map,
            file_dump=file_dump,
            check_duplicates=False,
        )

    def run(self, file_dump: str | None = None):
        """Run all processing steps."""
        self._check_geom()
        self.subset()
        self.clean()
        self.flag()
        self.reproject()
        self.populate_classification_table()
        self.import_to_db(file_dump=file_dump)

    def __call__(self, file_dump: str | None = None):
        """Allow instances to be called like functions."""
        self.run(file_dump=file_dump)
