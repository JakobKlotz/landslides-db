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
