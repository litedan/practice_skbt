"""Схемы персональных данных (ПД)."""

from datetime import date

from pydantic import Field

from app.schemas.common import ORMModel


class UserPrivateDataBase(ORMModel):
    passport: str | None = None
    inn: str | None = None
    snils: str | None = None
    bank_account: str | None = None
    military_id: str | None = None
    account_number: str | None = None
    bik: str | None = None
    bank_receiver: str | None = None
    correspondent_account: str | None = None
    kpp: str | None = None
    contract_number: str | None = None
    dismissal_date: date | None = None
    personal_data_deletion_date: date | None = None


class UserPrivateDataRead(UserPrivateDataBase):
    id: int
    user_id: int


class UserPrivateDataUpdate(UserPrivateDataBase):
    """PUT — частичное обновление ПД (все поля опциональны)."""

    pass
