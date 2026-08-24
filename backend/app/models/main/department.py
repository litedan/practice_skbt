"""Справочник отделов."""

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import MainBase


class Department(MainBase):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="department")
