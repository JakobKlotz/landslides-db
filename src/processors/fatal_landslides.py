import json
import warnings
from pathlib import Path

import geopandas as gpd

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
        )
        # Drop unused columns
        self.data = self.data[["Date", "description", "geometry"]].reset_index(
            drop=True
        )

        # Manually assign type (first and last one is a rockfall)
        warnings.warn(
            message="Caution: Types are manually assigned to the data."
            "If you have changed the source data of the global fatal landslide"
            " database check the results",
            stacklevel=2,
        )
        # Default type
        self.data["type"] = "landslide"
        # Those two events were rockfalls, see the description
        rockfall_dates = ["2005-08-23 00:00:00", "2008-03-01 00:00:00"]
        self.data.loc[self.data["Date"].isin(rockfall_dates), "type"] = (
            "rockfall"
        )

    def convert_crs(self):
        self.data = self.data.to_crs(crs=TARGET_CRS)
