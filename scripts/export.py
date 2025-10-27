# Connect to the db and export the landslide_view as GeoPackage
from pathlib import Path

import geopandas as gpd

from db.utils import create_db_session

out_path = Path("./db-dump")
out_path.mkdir(parents=True, exist_ok=True)
out_file = out_path / "landslides-db.gpkg"

Session = create_db_session()
with Session() as session:
    landslide_view = gpd.read_postgis(
        "SELECT * FROM landslides_view", session.bind, geom_col="geom"
    )
    landslide_view.to_file(out_file, driver="GPKG")
    print("Exported!")
