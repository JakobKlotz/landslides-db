# Dedicated import script
from pathlib import Path

from src.processors.fatal_landslides import GlobalFatalLandslides
from src.processors.geosphere import GeoSphere
from src.processors.nasa import Nasa
from src.processors.wlv import WLV

in_base_path, out_base_path = Path("./data/raw"), Path("./data/processed")

processors = [
    # GeoSphere must be first, to populate the classification table
    (GeoSphere, "geosphere/geosphere.gpkg"),
    (
        GlobalFatalLandslides,
        "global-fatal-landslides/global-fatal-landslides.gpkg",
    ),
    (Nasa, "nasa-coolr/nasa-coolr-reports-point.gpkg"),
    (WLV, "wlv/wlv.gpkg"),
]

for ProcClass, rel_path in processors:
    in_path = in_base_path / rel_path
    out_path = out_base_path / rel_path
    # create parent folders if they don't exist
    out_path.parent.mkdir(parents=True, exist_ok=True)

    proc = ProcClass(file_path=in_path)
    proc(file_dump=out_path)
