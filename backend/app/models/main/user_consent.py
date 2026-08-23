"""Согласия пользователей на обработку персональных данных."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import MainBase


class ConsentStatus(MainBase):
    """Справочник статусов согласия на обработку ПД."""

    __tablename__ = "consent_statuses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    consents: Mapped[list["UserConsent"]] = relationship(back_populates="consent_status")


class UserConsent(MainBase):
    __tablename__ = "user_consent"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_path: Mapped[str] = mapped_column(String(500), nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    signed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    consent_status_id: Mapped[int] = mapped_column(ForeignKey("consent_statuses.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="consents")
    consent_status: Mapped["ConsentStatus"] = relationship(back_populates="consents")
