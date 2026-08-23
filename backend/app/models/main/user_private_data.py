"""
Изолированное хранение персональных данных (ПД).

Доступ к этой таблице строго контролируется ролями
и логируется в sensitive_acces_log (LogBD).
"""

from datetime import date

from sqlalchemy import Date, ForeignKey, String
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

    passport: Mapped[str | None] = mapped_column(String(20))
    inn: Mapped[str | None] = mapped_column(String(12))
    snils: Mapped[str | None] = mapped_column(String(14))
    bank_account: Mapped[str | None] = mapped_column(String(20))
    reg_address: Mapped[str | None] = mapped_column(String(500))
    military_id: Mapped[str | None] = mapped_column(String(50))
    account_number: Mapped[str | None] = mapped_column(String(20))
    bik: Mapped[str | None] = mapped_column(String(9))
    bank_reliever: Mapped[str | None] = mapped_column(String(255))
    correspondent: Mapped[str | None] = mapped_column(String(20))
    kpp: Mapped[str | None] = mapped_column(String(9))
    contact_number: Mapped[str | None] = mapped_column(String(20))
    dismissal_date: Mapped[date | None] = mapped_column(Date)
    personal_date_deletion_date: Mapped[date | None] = mapped_column(Date)

    user: Mapped["User"] = relationship(back_populates="private_data")
