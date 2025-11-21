# Configuration

## De-Duplication: Change radius

Upon importing the data, a de-duplication process runs. By default, within a 
500 meter radius and the same event date, a duplicate is detected. This 
automatic duplicate check can have certain drawbacks. As mentioned in the 
[Limitations](../intro/about#important-limitations) section,
this might lead to imperfect duplicate detection as positional uncertainty must
be assumed. More practically, point geometries might have a higher positional
uncertainty than the default 500 meter radius. Thus, one might want to change
the radius.

After cloning the project, make changes to both functions `find_duplicate()` 
and `is_duplicated()` in `src/db/duplicates.py`. For example, increase the 
search radius from 500 to 1000 meters:

```python
def find_duplicate(  # [!code focus]
    session: Session,
    landslide_date: date,
    landslide_geom: WKTElement,
    search_radius_meters: int = 500,  # [!code --] [!code focus]
    search_radius_meters: int = 1000,  # [!code ++] [!code focus]
) -> Landslides | None:

...

def is_duplicated(  # [!code focus]
    session: Session,
    landslide_date: date,
    landslide_geom: WKTElement,
    search_radius_meters: int = 500,  # [!code --] [!code focus]
    search_radius_meters: int = 1000,  # [!code ++] [!code focus]
) -> bool:

...
```

After applying the changes, simply follow the [quick start guide](quick-start).

## PostGIS port

By default, the PostGIS data base is exposed on port `5432`. To change the port
navigate to the `.env` file and simply change the `POSTGRES_PORT` variable.
This example, changes the port from the default `5432` to `5173`.

```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432  # [!code --] [!code focus]
POSTGRES_PORT=5173  # [!code ++] [!code focus]
POSTGRES_DB=landslides
```

::: info

`docker-compose.yaml` will pick up the new `POSTGRES_PORT` variable. Be sure, 
to restart the `db` and `api` service!

```bash
docker compose restart db api
```

:::
