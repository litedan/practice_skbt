"""Изолированное хранение персональных данных (ПД)."""

from datetime import date

from sqlalchemy import Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import MainBase


class UserPrivateData(MainBase):
    __tablename__ = "user_private_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    passport: Mapped[str | None] = mapped_column(Text)
    inn: Mapped[str | None] = mapped_column(Text)
    snils: Mapped[str | None] = mapped_column(Text)
    bank_account: Mapped[str | None] = mapped_column(Text)
    military_id: Mapped[str | None] = mapped_column(Text)
    account_number: Mapped[str | None] = mapped_column(Text)
    bik: Mapped[str | None] = mapped_column(Text)
    bank_receiver: Mapped[str | None] = mapped_column(Text)
    correspondent_account: Mapped[str | None] = mapped_column(Text)
    kpp: Mapped[str | None] = mapped_column(Text)
    contract_number: Mapped[str | None] = mapped_column(Text)
    dismissal_date: Mapped[date | None] = mapped_column(Date)
    personal_data_deletion_date: Mapped[date | None] = mapped_column(Date)

    user: Mapped["User"] = relationship(back_populates="private_data")
