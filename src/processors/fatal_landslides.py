import json
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from src.constants import AUSTRIA, TARGET_CRS


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
            "Trigger: "
            + self.data["Trigger"]
            + "; Report: "
            + self.data["Report_1"]
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
        print(self.data)
        # A spatial match is only valid if the dates also match.
        # Invalidate matches where the dates are different.
        date_mismatch = self.data["Date_left"] != self.data["Date_right"]
        self.data.loc[date_mismatch, "type_override"] = None

        # All other events are landslides (the default)
        self.data["type"] = self.data["type_override"].fillna("landslide")
        # Drop helper columns from the join
        self.data = self.data.drop(
            columns=["type_override", "index_right", "Date_right"]
        ).rename(columns={"Date_left": "Date"})
