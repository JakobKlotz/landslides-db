from datetime import date

from geoalchemy2.functions import ST_DWithin
from geoalchemy2.shape import WKTElement
from sqlalchemy.orm import Session

from src.models import Landslides


def find_duplicate(
    session: Session,
    landslide_date: date,
    landslide_geom: WKTElement,
    search_radius_meters: int = 1_000,
) -> Landslides | None:
    """
    Checks for existing landslides at the same date within a given radius.

    Args:
        session (Session): Active SQLAlchemy session used to execute the query.
        landslide_date (date): Date of the new landslide; only records with the
            same date are considered.
        landslide_geom (WKTElement): WKTElement representing the new
            landslide's geometry (must be in the same spatial reference as
            stored geometries).
        search_radius_meters (int, optional): Radius in meters within which an
            existing landslide is considered a potential duplicate. Defaults to
            1_000.
    Returns:
        Landslides | None: The first matching Landslides instance if a
        potential duplicate is found; otherwise None.
    """
    return (
        session.query(Landslides)
        .filter(
            Landslides.date == landslide_date,
            ST_DWithin(Landslides.geom, landslide_geom, search_radius_meters),
        )
        .first()
    )


def is_duplicated(
    session: Session,
    landslide_date: date,
    landslide_geom: WKTElement,
    search_radius_meters: int = 1_000,
) -> bool:
    """
    Boolean check for an existing event at the same date within a given radius.

    Args:
        session (Session): Active SQLAlchemy session used to execute the query.
        landslide_date (date): Date of the new landslide; only records with the
            same date are considered.
        landslide_geom (WKTElement): WKTElement representing the new
            landslide's geometry (must be in the same spatial reference as
            stored geometries).
        search_radius_meters (int, optional): Radius in meters within which an
            existing landslide is considered a potential duplicate. Defaults to
            1_000.
    Returns:
        bool: True if a potential duplicate is found; otherwise False.
    """
    result = find_duplicate(
        session,
        landslide_date,
        landslide_geom,
        search_radius_meters,
    )

    return result is not None
