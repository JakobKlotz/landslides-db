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


def dump_gpkg(
    data: gpd.GeoDataFrame,
    output_file: str | Path,
    overwrite: bool = True,
) -> None:
    """Dump the processed data to a file."""
    if Path(output_file).exists() and not overwrite:
        raise FileExistsError(
            f"File {output_file} already exists. Skipping dump. "
            f"Set overwrite=True to overwrite."
        )
    # delete an existing GeoPackage, overwriting leads to issues
    Path(output_file).unlink(missing_ok=True)
    data.to_file(output_file, driver="GPKG")
