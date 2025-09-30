from datetime import date
from typing import List, Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    ForeignKey,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.constants import TARGET_CRS


class Base(DeclarativeBase):
    pass


class Landslides(Base):
    __tablename__ = "landslides"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[Optional[str]] = mapped_column(String(60))
    date: Mapped[date]
    report: Mapped[Optional[str]]
    report_source: Mapped[Optional[str]]
    report_url: Mapped[Optional[str]]

    # Point geom must always be present, if Polygon given, calculate the
    # centroid
    geom: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=TARGET_CRS)
    )
    polygon_geom: Mapped[Optional[Geometry]] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=TARGET_CRS)
    )

    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    source: Mapped["Sources"] = relationship(back_populates="landslides")

    # No UniqueConstraint - that's handled by the import logic
    # The combination of date & geom within a certain radius defines a unique
    # record


class Sources(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    downloaded: Mapped[date]
    modified: Mapped[Optional[date]]
    license: Mapped[str]
    url: Mapped[str]
    description: Mapped[Optional[str]]
    doi: Mapped[Optional[str]]

    landslides: Mapped[List["Landslides"]] = relationship(
        back_populates="source"
    )
