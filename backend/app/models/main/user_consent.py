"""Согласия пользователей на обработку персональных данных."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import MainBase


class ConsentStatus(MainBase):
    __tablename__ = "consent_statuses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    consents: Mapped[list["UserConsent"]] = relationship(back_populates="consent_status")


class UserConsent(MainBase):
    __tablename__ = "user_consent"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_path: Mapped[str | None] = mapped_column(Text)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valid_until: Mapped[date | None] = mapped_column(Date)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    consent_status_id: Mapped[int] = mapped_column(
        ForeignKey("consent_statuses.id", ondelete="SET NULL"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="consents")
    consent_status: Mapped["ConsentStatus"] = relationship(back_populates="consents")
