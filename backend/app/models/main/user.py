"""
Модель пользователя (MainBD).

Персональные и чувствительные данные вынесены в UserPrivateData (1:1)
для изоляции ПД согласно требованиям законодательства.
"""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import MainBase


class User(MainBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    birth_date: Mapped[date | None] = mapped_column(Date)
    city: Mapped[str | None] = mapped_column(String(100))
    hire_date: Mapped[date | None] = mapped_column(Date)

    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    block_reason: Mapped[str | None] = mapped_column(Text)

    department_id: Mapped[int | None] = mapped_column(ForeignKey("departaments_list.id"))
    position_id: Mapped[int | None] = mapped_column(ForeignKey("position_list.id"))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False, index=True)

    # --- Связи ---
    role: Mapped["Role"] = relationship(back_populates="users")
    department: Mapped["Department | None"] = relationship(back_populates="users")
    position: Mapped["Position | None"] = relationship(back_populates="users")
    private_data: Mapped["UserPrivateData | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    created_requests: Mapped[list["Request"]] = relationship(
        back_populates="creator",
        foreign_keys="Request.creator_id",
    )
    checked_requests: Mapped[list["Request"]] = relationship(
        back_populates="checker",
        foreign_keys="Request.checker_id",
    )
    consents: Mapped[list["UserConsent"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
