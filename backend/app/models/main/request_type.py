"""Справочник типов кадровых заявок."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import MainBase


class RequestType(MainBase):
    __tablename__ = "request_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(500))

    requests: Mapped[list["Request"]] = relationship(back_populates="request_type")
