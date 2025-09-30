from pathlib import Path

import geopandas as gpd
import pandas as pd

from src.constants import AUSTRIA, TARGET_CRS
from src.processors.base import BaseProcessor


class Nasa(BaseProcessor):
    """Import NASA COOLR landslide report points."""

    def __init__(self, *, file_path: str | Path):
        super().__init__(file_path=file_path, dataset_name="NASA COOLR")
        # Ensure that points are within Austria
        # CRS mis-match between the two files is handled internally by
        # geopandas
        self.data = gpd.read_file(file_path, mask=AUSTRIA)

    def clean(self):
        """Subset the data"""
        # Date must be given
        self.data = self.data[~self.data["event_date"].isna()]
        # Remove newlines
        self.data["event_desc"] = self.data["event_desc"].str.replace(
            "\n", " "
        )

        columns_to_keep = [
            "event_desc",  # report
            "source_lin",  # also to comply with the license
            "source_nam",  # comply with the license
            "event_date",
            "landslide_",
            "geometry",
        ]
        self.data = self.data[columns_to_keep]

        # Map categories; GeoSphere types are used as basis:
        # ['gravity slide or flow' 'mass movement (undefined type)' 'rockfall'
        # 'collapse, sinkhole' 'deep seated rock slope deformation']
        type_mapping = {
            # term landslide is very general and doesn't specify any type
            # of movement -> mass movement
            "landslide": "mass movement (undefined type)",
            "mudslide": "gravity slide or flow",
            "rock_fall": "rockfall",
            "topple": "rockfall",
            "debris_flow": "gravity slide or flow",
            # is dropped
            "snow_avalanche": None,
        }

        types = []
        for cat in self.data["landslide_"]:
            try:
                types.append(type_mapping[cat])
            except KeyError as err:
                raise UserWarning(
                    f"New category {cat} encountered!\nCheck the type mapping"
                ) from err
        self.data["type"] = types

        # Remove all events with no type
        self.data = self.data[~self.data["type"].isna()]
        # convert datetime64[ns] -> python date objects
        self.data["event_date"] = pd.to_datetime(
            self.data["event_date"]
        ).dt.date

        # Project to target CRS
        self.data = self.data.to_crs(crs=TARGET_CRS)

    def import_to_db(self, file_dump: str | None = None):
        """Import to PostGIS database."""
        column_map = {
            "type": "type",
            "date": "event_date",
            "description": "description",
            "report": "event_desc",
            "report_source": "source_nam",
            "report_url": "source_lin",
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
