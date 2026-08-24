"""Справочник типов кадровых заявок."""

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import MainBase


class RequestType(MainBase):
    __tablename__ = "request_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    file_path: Mapped[str | None] = mapped_column(Text)

    requests: Mapped[list["Request"]] = relationship(back_populates="request_type")
