"""Кадровые заявки сотрудников."""

from datetime import date

from sqlalchemy import Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import MainBase
from app.models.mixins import TimestampMixin


class Request(MainBase, TimestampMixin):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment: Mapped[str | None] = mapped_column(Text)
    date_from: Mapped[date | None] = mapped_column(Date)
    date_to: Mapped[date | None] = mapped_column(Date)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    checker_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"), nullable=False)
    request_type_id: Mapped[int] = mapped_column(ForeignKey("request_types.id"), nullable=False)

    creator: Mapped["User"] = relationship(
        back_populates="created_requests",
        foreign_keys=[creator_id],
    )
    checker: Mapped["User | None"] = relationship(
        back_populates="checked_requests",
        foreign_keys=[checker_id],
    )
    status: Mapped["Status"] = relationship(back_populates="requests")
    request_type: Mapped["RequestType"] = relationship(back_populates="requests")
    document_files: Mapped[list["DocumentFile"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(back_populates="request")
