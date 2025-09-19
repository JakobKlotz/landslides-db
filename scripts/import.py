from pathlib import Path

import geopandas as gpd
import pandas as pd
from constants import TARGET_CRS


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
        self.data = self.data.sort_values(by="validFrom", ascending=False)

        def _remove_duplicates(self):
            # remove all *obvious* duplicates, keep most recent entry
            self.data = self.data.drop_duplicates(
                subset=["validFrom", "description", "geometry"], keep="last"
            )
            # remove entries with no valid date (validFrom) among the duplicates
            # get all remaining duplicates by geometry
            dup = self.data[
                self.data.duplicated(subset="geometry", keep=False)
            ].sort_values(by=["geometry", "validFrom"])
            # remove all entries with no validFrom date *among the duplicates*
            ids = dup[dup["validFrom"].isna()]["inspireId_localId"]
            # drop them from the original data set
            self.data = self.data[~self.data["inspireId_localId"].isin(ids)]

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
            f"likely errors with a {days}-day threshold."
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

    def run(self, dump: str | None = None):
        """Run all processing steps."""
        self._check_geom()
        self.subset()
        self._clean()
        self._flag()
        self.reproject()

        if dump:
            self.dump(dump)
