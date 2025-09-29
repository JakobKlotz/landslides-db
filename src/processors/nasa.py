import json
from pathlib import Path

import geopandas as gpd

from constants import AUSTRIA


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

        # Map categories
        categories = {
            "landslide": "landslide",
            "mudslide": "",
            "rock_fall": "rockfall",
            "debris_flow": "",
            "snow_avalanche": None,
            "topple": "",
        }

        types = []
        for cat in self.data["landslide_"]:
            try:
                types.append(categories[cat])
            except KeyError as err:
                raise UserWarning(f"New category {cat} encountered!") from err
        self.data["type"] = types

        # Remove all events with no type
        self.data = self.data[~self.data["type"].isna()]
