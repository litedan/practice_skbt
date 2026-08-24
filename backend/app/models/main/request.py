"""Кадровые заявки сотрудников."""

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import MainBase
from app.models.mixins import TimestampMixin


class Request(MainBase, TimestampMixin):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment: Mapped[str | None] = mapped_column(Text)

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    approver_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    status_id: Mapped[int] = mapped_column(
        ForeignKey("statuses.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    request_type_id: Mapped[int] = mapped_column(
        ForeignKey("request_types.id", ondelete="SET NULL"),
        nullable=False,
    )

    employee: Mapped["User"] = relationship(
        back_populates="employee_requests",
        foreign_keys=[employee_id],
    )
    reviewer: Mapped["User | None"] = relationship(
        back_populates="reviewed_requests",
        foreign_keys=[reviewer_id],
    )
    approver: Mapped["User | None"] = relationship(
        back_populates="approved_requests",
        foreign_keys=[approver_id],
    )
    status: Mapped["Status"] = relationship(back_populates="requests")
    request_type: Mapped["RequestType"] = relationship(back_populates="requests")
    document_files: Mapped[list["DocumentFile"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(back_populates="request")
