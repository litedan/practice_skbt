"""Справочник должностей (также определяет роль в RBAC)."""

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import MainBase


class Position(MainBase):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="position")
