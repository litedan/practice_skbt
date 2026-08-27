"""Схемы персональных данных (ПД)."""

from datetime import date
from typing import Any

from pydantic import field_validator, model_validator

from app.core.private_data_validation import (
    normalize_account_number,
    normalize_bank_receiver,
    normalize_bik,
    normalize_inn,
    normalize_kpp,
    normalize_military_id,
    normalize_passport,
    normalize_snils,
)
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

    @field_validator("passport", mode="before")
    @classmethod
    def _passport(cls, value: Any) -> str | None:
        return normalize_passport(value if value is None else str(value))

    @field_validator("snils", mode="before")
    @classmethod
    def _snils(cls, value: Any) -> str | None:
        return normalize_snils(value if value is None else str(value))

    @field_validator("inn", mode="before")
    @classmethod
    def _inn(cls, value: Any) -> str | None:
        return normalize_inn(value if value is None else str(value))

    @field_validator("military_id", mode="before")
    @classmethod
    def _military(cls, value: Any) -> str | None:
        return normalize_military_id(value if value is None else str(value))

    @field_validator("account_number", mode="before")
    @classmethod
    def _account(cls, value: Any) -> str | None:
        return normalize_account_number(
            value if value is None else str(value),
            label="Номер счёта",
        )

    @field_validator("correspondent_account", mode="before")
    @classmethod
    def _corr(cls, value: Any) -> str | None:
        return normalize_account_number(
            value if value is None else str(value),
            label="Корр. счёт",
        )

    @field_validator("bank_account", mode="before")
    @classmethod
    def _bank_account(cls, value: Any) -> str | None:
        return normalize_account_number(
            value if value is None else str(value),
            label="Банковский счёт",
        )

    @field_validator("bik", mode="before")
    @classmethod
    def _bik(cls, value: Any) -> str | None:
        return normalize_bik(value if value is None else str(value))

    @field_validator("kpp", mode="before")
    @classmethod
    def _kpp(cls, value: Any) -> str | None:
        return normalize_kpp(value if value is None else str(value))

    @field_validator("bank_receiver", mode="before")
    @classmethod
    def _bank_receiver(cls, value: Any) -> str | None:
        return normalize_bank_receiver(value if value is None else str(value))

    @model_validator(mode="after")
    def _strip_blank_contract(self) -> "UserPrivateDataUpdate":
        if self.contract_number is not None and not str(self.contract_number).strip():
            self.contract_number = None
        return self
