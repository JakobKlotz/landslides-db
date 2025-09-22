# Dedicated import script
from src.processors.geosphere import GeoSphere


def import_data():
    geosphere = GeoSphere(
        file_path="data/raw/geosphere.gpkg",
        metadata_file="data/raw/geosphere.meta.json",
    )
    geosphere.run(file_dump="data/processed/geosphere.gpkg")


import_data()
