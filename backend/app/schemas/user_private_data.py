"""Схемы персональных данных (ПД)."""

from datetime import date

from pydantic import Field

from app.schemas.common import ORMModel


class UserPrivateDataBase(ORMModel):
    passport: str | None = Field(default=None, max_length=20)
    inn: str | None = Field(default=None, max_length=12)
    snils: str | None = Field(default=None, max_length=14)
    bank_account: str | None = Field(default=None, max_length=20)
    reg_address: str | None = Field(default=None, max_length=500)
    military_id: str | None = Field(default=None, max_length=50)
    account_number: str | None = Field(default=None, max_length=20)
    bik: str | None = Field(default=None, max_length=9)
    bank_reliever: str | None = Field(default=None, max_length=255)
    correspondent: str | None = Field(default=None, max_length=20)
    kpp: str | None = Field(default=None, max_length=9)
    contact_number: str | None = Field(default=None, max_length=20)
    dismissal_date: date | None = None
    personal_date_deletion_date: date | None = None


class UserPrivateDataRead(UserPrivateDataBase):
    id: int
    user_id: int


class UserPrivateDataUpdate(UserPrivateDataBase):
    """PUT — частичное обновление ПД (все поля опциональны)."""
    pass
