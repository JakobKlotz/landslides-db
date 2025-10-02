# Dedicated import script
from pathlib import Path

from src.processors.fatal_landslides import GlobalFatalLandslides
from src.processors.geosphere import GeoSphere
from src.processors.nasa import Nasa
from src.processors.wlv import WLV


def import_data():
    in_base_path, out_base_path = Path("./data/raw"), Path("./data/processed")
    # -------------------------------------------------------------------------
    # GeoSphere
    # -------------------------------------------------------------------------
    geosphere = GeoSphere(
        file_path=in_base_path / "geosphere/geosphere.gpkg",
    )
    geosphere.run(file_dump=out_base_path / "geosphere/geosphere.gpkg")

    # -------------------------------------------------------------------------
    # Global Fatal Landslides
    # -------------------------------------------------------------------------
    fatal_landslides = GlobalFatalLandslides(
        file_path=in_base_path
        / "global-fatal-landslides/global-fatal-landslides.gpkg",
    )
    fatal_landslides.run(
        file_dump=out_base_path
        / "global-fatal-landslides/global-fatal-landslides.gpkg"
    )

    # -------------------------------------------------------------------------
    # NASA COOLR reports points
    # -------------------------------------------------------------------------
    nasa = Nasa(
        file_path=in_base_path / "nasa-coolr/nasa-coolr-reports-point.gpkg",
    )
    nasa.run(
        file_dump=out_base_path / "nasa-coolr/nasa-coolr-reports-point.gpkg"
    )

    # -------------------------------------------------------------------------
    # WLV
    # -------------------------------------------------------------------------
    wlv = WLV(file_path=in_base_path / "wlv/wlv.gpkg")
    wlv.run(file_dump=out_base_path / "wlv/wlv.gpkg")


import_data()
