"""Валидация и нормализация персональных / банковских реквизитов РФ."""

from __future__ import annotations

import re

_DIGITS = re.compile(r"\D+")
_MILITARY = re.compile(r"^([А-ЯA-Z]{2})\s*(\d{6,8})$", re.IGNORECASE)


def _digits_only(value: str) -> str:
    return _DIGITS.sub("", value)


def _empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def normalize_passport(value: str | None) -> str | None:
    value = _empty_to_none(value)
    if value is None:
        return None
    digits = _digits_only(value)
    if len(digits) != 10:
        raise ValueError("Паспорт: ожидается 10 цифр (серия и номер)")
    return f"{digits[:4]} {digits[4:]}"


def normalize_snils(value: str | None) -> str | None:
    value = _empty_to_none(value)
    if value is None:
        return None
    digits = _digits_only(value)
    if len(digits) != 11:
        raise ValueError("СНИЛС: ожидается 11 цифр")
    if not _snils_checksum_ok(digits):
        raise ValueError("СНИЛС: неверная контрольная сумма")
    return f"{digits[:3]}-{digits[3:6]}-{digits[6:9]} {digits[9:]}"


def normalize_inn(value: str | None) -> str | None:
    value = _empty_to_none(value)
    if value is None:
        return None
    digits = _digits_only(value)
    if len(digits) not in (10, 12):
        raise ValueError("ИНН: ожидается 10 или 12 цифр")
    if not _inn_checksum_ok(digits):
        raise ValueError("ИНН: неверная контрольная сумма")
    return digits


def normalize_military_id(value: str | None) -> str | None:
    value = _empty_to_none(value)
    if value is None:
        return None
    compact = re.sub(r"\s+", "", value).upper()
    match = _MILITARY.match(compact)
    if match:
        series, number = match.groups()
        return f"{series.upper()} {number}"
    digits = _digits_only(value)
    if len(digits) in (6, 7, 8) and digits == compact:
        return digits
    raise ValueError(
        "Военный билет: ожидается серия (2 буквы) и номер (6–8 цифр), "
        "например «АБ 1234567»"
    )


def normalize_account_number(value: str | None, *, label: str = "Номер счёта") -> str | None:
    value = _empty_to_none(value)
    if value is None:
        return None
    digits = _digits_only(value)
    if len(digits) != 20:
        raise ValueError(f"{label}: ожидается 20 цифр")
    return digits


def normalize_bik(value: str | None) -> str | None:
    value = _empty_to_none(value)
    if value is None:
        return None
    digits = _digits_only(value)
    if len(digits) != 9:
        raise ValueError("БИК: ожидается 9 цифр")
    return digits


def normalize_kpp(value: str | None) -> str | None:
    value = _empty_to_none(value)
    if value is None:
        return None
    digits = _digits_only(value)
    if len(digits) != 9:
        raise ValueError("КПП: ожидается 9 цифр")
    return digits


def normalize_bank_receiver(value: str | None) -> str | None:
    value = _empty_to_none(value)
    if value is None:
        return None
    if len(value) < 3:
        raise ValueError("Банк получатель: слишком короткое название")
    if len(value) > 200:
        raise ValueError("Банк получатель: слишком длинное название")
    return value


def _snils_checksum_ok(digits: str) -> bool:
    body = [int(c) for c in digits[:9]]
    control = int(digits[9:])
    total = sum(n * (9 - i) for i, n in enumerate(body))
    if total < 100:
        expected = total
    elif total in (100, 101):
        expected = 0
    else:
        expected = total % 101
        if expected == 100:
            expected = 0
    return control == expected


def _inn_checksum_ok(digits: str) -> bool:
    nums = [int(c) for c in digits]

    def check(weights: tuple[int, ...], value: list[int]) -> int:
        return sum(w * d for w, d in zip(weights, value, strict=False)) % 11 % 10

    if len(nums) == 10:
        return check((2, 4, 10, 3, 5, 9, 4, 6, 8), nums[:9]) == nums[9]
    n11 = check((7, 2, 4, 10, 3, 5, 9, 4, 6, 8), nums[:10])
    n12 = check((3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8), nums[:11])
    return n11 == nums[10] and n12 == nums[11]
