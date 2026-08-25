"""
Модель пользователя (MainBD).

Роль в системе определяется должностью (positions):
Работник / HR / Руководитель / Администратор.
"""

from datetime import date

from sqlalchemy import Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import MainBase


class User(MainBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phone: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    birth_date: Mapped[date | None] = mapped_column(Date)
    city: Mapped[str | None] = mapped_column(Text)
    hire_date: Mapped[date | None] = mapped_column(Date)
    blocked_at: Mapped[date | None] = mapped_column(Date)
    block_reason: Mapped[str | None] = mapped_column(Text)

    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"),
        index=True,
    )
    position_id: Mapped[int | None] = mapped_column(
        ForeignKey("positions.id", ondelete="SET NULL"),
        index=True,
    )

    department: Mapped["Department | None"] = relationship(back_populates="users")
    position: Mapped["Position | None"] = relationship(back_populates="users")
    private_data: Mapped["UserPrivateData | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    employee_requests: Mapped[list["Request"]] = relationship(
        back_populates="employee",
        foreign_keys="Request.employee_id",
    )
    reviewed_requests: Mapped[list["Request"]] = relationship(
        back_populates="reviewer",
        foreign_keys="Request.reviewer_id",
    )
    approved_requests: Mapped[list["Request"]] = relationship(
        back_populates="approver",
        foreign_keys="Request.approver_id",
    )
    consents: Mapped[list["UserConsent"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")

    @property
    def is_blocked(self) -> bool:
        return self.blocked_at is not None
