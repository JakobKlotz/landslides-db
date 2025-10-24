# Sets CRS as constant which is used for all data base records
from importlib.resources import files
from pathlib import Path

import geopandas as gpd

TARGET_CRS = 32632
TARGET_CRS_SRS = "EPSG:32632"


def _read_austrian_border(
    input_file: str | Path = None,
    to_target_crs: bool = True,
) -> gpd.GeoDataFrame:
    """From an Eurostat NUTS file:
    https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics
    """
    if input_file is None:
        # Load from package resources
        input_file = files().joinpath("data/NUTS_RG_03M_2024_4326.gpkg")

    data = gpd.read_file(input_file)
    austria = data.query("CNTR_CODE == 'AT' and LEVL_CODE == 0").reset_index(
        drop=True
    )
    austria = austria[["NUTS_ID", "NAME_LATN", "geometry"]]
    if to_target_crs:
        austria = austria.to_crs(TARGET_CRS)

    return austria


AUSTRIA = _read_austrian_border()
