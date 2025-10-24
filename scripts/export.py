# Connect to the db and export the landslide_view as GeoPackage
import geopandas as gpd

from db.utils import create_db_session

out_file = "landslides-db"

Session = create_db_session()
with Session() as session:
    landslide_view = gpd.read_postgis(
        "SELECT * FROM landslides_view", session.bind, geom_col="geom"
    )
    landslide_view.to_file(f"{out_file}.gpkg", driver="GPKG")
    print("Exported!")

    landslide_view.source_name.value_counts().to_csv(
        f"{out_file}.csv", index=True
    )
