from datetime import date
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    List,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

TARGET_CRS = 32632


class Base(DeclarativeBase):
    pass


class Landslides(Base):
    __tablename__ = "landslides"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[Optional[str]] = mapped_column(String(60))
    description: Mapped[Optional[str]]

    # Point geom must always be present, if Polygon given, calculate the
    # centroid
    geom: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=TARGET_CRS)
    )
    polygon_geom: Optional[Mapped[Geometry]] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=TARGET_CRS)
    )

    source: Mapped["Sources"] = relationship(back_populates="landslides")


class Sources(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    downloaded: Mapped[date]
    modified: Mapped[Optional[date]]
    license: Mapped[str]
    url: Mapped[str]

    landslides: Mapped[List["Landslides"]] = relationship(
        back_populates="source"
    )
