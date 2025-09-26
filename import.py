# Dedicated import script
from pathlib import Path

from src.processors.fatal_landslides import GlobalFatalLandslides
from src.processors.geosphere import GeoSphere


def import_data():
    in_base_path, out_base_path = Path("./data/raw"), Path("./data/processed")
    # -------------------------------------------------------------------------
    # GeoSphere
    # -------------------------------------------------------------------------
    geosphere = GeoSphere(
        file_path=in_base_path / "geosphere/geosphere.gpkg",
        metadata_file=in_base_path / "geosphere/geosphere.meta.json",
    )
    geosphere.run(file_dump=out_base_path / "geosphere/geosphere.gpkg")

    # -------------------------------------------------------------------------
    # Global Fatal Landslides
    # -------------------------------------------------------------------------
    fatal_landslides = GlobalFatalLandslides(
        file_path=in_base_path
        / "global-fatal-landslides/global-fatal-landslides.gpkg",
        metadata_file=in_base_path
        / "global-fatal-landslides/global-fatal-landslides.meta.json",
    )
    fatal_landslides.run(
        file_dump=out_base_path
        / "global-fatal-landslides/global-fatal-landslides.gpkg"
    )


import_data()
