from pathlib import Path

import pandas as pd

from db.processors.base import BaseProcessor


class WLV(BaseProcessor):
    """Wildbach- und Lawinenverbauung data set."""

    def __init__(self, *, file_path: str | Path):
        super().__init__(
            file_path=file_path, dataset_name="Wildbach- und Lawinenverbauung"
        )

    def _build_categories(self):
        """Extract the WLV categories from their description string."""
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

    def _filter_debris_flows(self):
        """Get all debris flows within the Water ('Wasser') category."""
        debris_flows = self.data[self.data["category"] == "Wasser"]

        # filter by subcategories Murgang & Murartiger Feststofftransport
        debris_flows["subcategory"] = (
            self.data["nameOfEvent"]
            .str.partition("-")[0]
            .str.partition(":")[2]
            .str.strip()
        )

        expected_water_subcategories = set(
            [
                "Hochwasser",
                "Fluviatiler Feststofftransport",
                "Murgang",
                "Murartiger Feststofftransport",
                "Oberflächenabfluss",
            ]
        )

        unexpected_water_subcategories = set(
            debris_flows["subcategory"].unique()
        ).difference(expected_water_subcategories)

        if unexpected_water_subcategories:
            raise ValueError(
                f"Unexpected subcategories found in Water entries: "
                f"{unexpected_water_subcategories}"
            )

        # Filter by Murgang & Murartiger Feststofftransport
        return debris_flows[
            debris_flows["subcategory"].isin(
                ("Murgang", "Murartiger Feststofftransport")
            )
        ]

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

        # Get WLV categories
        self._build_categories()

        # Get all debris flows
        debris_flows = self._filter_debris_flows()

        # Keep slides and rockfalls
        self.data = self.data[
            self.data["category"].isin(("Rutschung", "Steinschlag"))
        ]

        # Append debris flows
        self.data = pd.concat(
            [self.data, debris_flows], axis=0, ignore_index=True
        )

        # Map them to the GeoSphere classifications
        self.data["classification"] = self.data["category"].replace(
            {
                "Rutschung": "gravity slide or flow",
                "Steinschlag": "rockfall",
                # 'Wasser' has only the subcategories
                # Murgang & Murartiger Feststofftransport remaining
                "Wasser": "gravity slide or flow",
            }
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
