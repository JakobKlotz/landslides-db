from pathlib import Path

import geopandas as gpd


def convert_to_gpkg(
    *, input_file: str | Path, output_file: str | Path
) -> None:
    supported_formats = (".shp", ".geojson", ".gml")
    if Path(input_file).suffix not in supported_formats:
        raise ValueError(
            f"Input file is not supported."
            f" Supported formats are: {supported_formats}"
        )

    gpd.read_file(input_file).to_file(output_file, driver="GPKG")
    print("Converted!")
