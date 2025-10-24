from pathlib import Path

import geopandas as gpd
import pandas as pd

from db.processors.base import BaseProcessor


class WLV(BaseProcessor):
    """Wildbach- und Lawinenverbauung data set."""

    def __init__(self, *, file_path: str | Path):
        super().__init__(
            file_path=file_path, dataset_name="Wildbach- und Lawinenverbauung"
        )
        # mask is not strictly necessary (left in for a unified approach)
        self.data = gpd.read_file(file_path, mask=self.austria).to_crs(
            crs=self.target_crs
        )

    def clean(self):
        """Subset and clean the data."""
        # Remove all "unbekannt" dates
        self.data = self.data[self.data["validFrom"] != "unbekannt"]
        # validFrom to date (coerce - historical dates are in there)
        self.data["validFrom"] = pd.to_datetime(
            self.data["validFrom"], errors="coerce"
        ).dt.date
        # Remove all entries with no date
        self.data = self.data[~self.data["validFrom"].isna()]

        # Extract broad classification
        self.data["category"] = self.data["nameOfEvent"].str.split(": ").str[0]

        # Sanity check
        expected_categories = set(
            ["Wasser", "Lawine", "Rutschung", "Steinschlag"]
        )
        unexpected_categories = set(self.data["category"].unique()).difference(
            expected_categories
        )
        if unexpected_categories:
            raise ValueError(
                f"Unexpected categories found: {unexpected_categories}"
            )
        # Keep slides and rockfalls
        self.data = self.data[
            self.data["category"].isin(("Rutschung", "Steinschlag"))
        ]
        # Map them to the GeoSphere classifications
        self.data["classification"] = self.data["category"].replace(
            {"Rutschung": "gravity slide or flow", "Steinschlag": "rockfall"}
        )

        # Subset
        self.data = self.data[["classification", "validFrom", "geometry"]]

    def import_to_db(self, file_dump: str | None = None):
        column_map = {
            "classification": "classification",
            "date": "validFrom",
        }

        self._import_to_db(
            data_to_import=self.data,
            column_map=column_map,
            file_dump=file_dump,
            check_duplicates=True,
        )

    def run(self, file_dump: str | None = None):
        """Run all processing steps."""
        self.clean()
        self.import_to_db(file_dump=file_dump)

    def __call__(self, file_dump: str | None = None):
        """Allow instances to be called like functions."""
        self.run(file_dump=file_dump)
