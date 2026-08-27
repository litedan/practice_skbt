/** Клиентская валидация ПДн / банковских реквизитов (зеркало backend). */

export type PrivateFieldKey =
  | 'passport'
  | 'military_id'
  | 'inn'
  | 'snils'
  | 'account_number'
  | 'correspondent_account'
  | 'bik'
  | 'kpp'
  | 'bank_receiver'
  | 'bank_account'

function digitsOnly(value: string) {
  return value.replace(/\D+/g, '')
}

function emptyToNull(value: string | null | undefined): string | null {
  if (value == null) return null
  const cleaned = value.trim()
  return cleaned || null
}

function snilsChecksumOk(digits: string) {
  const body = digits.slice(0, 9).split('').map(Number)
  const control = Number(digits.slice(9))
  const total = body.reduce((sum, n, i) => sum + n * (9 - i), 0)
  let expected: number
  if (total < 100) expected = total
  else if (total === 100 || total === 101) expected = 0
  else {
    expected = total % 101
    if (expected === 100) expected = 0
  }
  return control === expected
}

function innChecksumOk(digits: string) {
  const nums = digits.split('').map(Number)
  const check = (weights: number[], value: number[]) =>
    weights.reduce((sum, w, i) => sum + w * value[i], 0) % 11 % 10

  if (nums.length === 10) {
    return check([2, 4, 10, 3, 5, 9, 4, 6, 8], nums.slice(0, 9)) === nums[9]
  }
  const n11 = check([7, 2, 4, 10, 3, 5, 9, 4, 6, 8], nums.slice(0, 10))
  const n12 = check([3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8], nums.slice(0, 11))
  return n11 === nums[10] && n12 === nums[11]
}

/** Пока поле вводится — мягкие подсказки; полная проверка при blur/submit. */
export function validatePrivateField(
  key: PrivateFieldKey,
  raw: string | null | undefined,
  opts: { strict?: boolean } = {},
): string | null {
  const strict = opts.strict ?? true
  const value = emptyToNull(raw)
  if (value == null) return null

  switch (key) {
    case 'passport': {
      const digits = digitsOnly(value)
      if (!strict && digits.length < 10) {
        if (/\D/.test(value.replace(/\s/g, '')) && !/^\d[\d\s]*$/.test(value)) {
          return 'Только цифры (серия и номер)'
        }
        return null
      }
      if (digits.length !== 10) return 'Ожидается 10 цифр (серия и номер)'
      return null
    }
    case 'snils': {
      const digits = digitsOnly(value)
      if (!strict && digits.length < 11) {
        if (/[^\d\-\s]/.test(value)) return 'Только цифры'
        return null
      }
      if (digits.length !== 11) return 'Ожидается 11 цифр'
      if (!snilsChecksumOk(digits)) return 'Неверная контрольная сумма'
      return null
    }
    case 'inn': {
      const digits = digitsOnly(value)
      if (!strict && digits.length < 10) {
        if (/\D/.test(value)) return 'Только цифры'
        return null
      }
      if (digits.length !== 10 && digits.length !== 12) return 'Ожидается 10 или 12 цифр'
      if (!innChecksumOk(digits)) return 'Неверная контрольная сумма'
      return null
    }
    case 'military_id': {
      const compact = value.replace(/\s+/g, '').toUpperCase()
      const withSeries = /^[А-ЯA-Z]{2}\d{6,8}$/i.test(compact)
      const digitsOnlyId = /^\d{6,8}$/.test(compact)
      if (!strict) {
        if (compact.length < 6) return null
        if (/^[А-ЯA-Z]{1,2}$/i.test(compact)) return null
        if (/^[А-ЯA-Z]{2}\d{0,5}$/i.test(compact)) return null
        if (/^\d{1,5}$/.test(compact)) return null
      }
      if (withSeries || digitsOnlyId) return null
      return 'Серия (2 буквы) и номер (6–8 цифр), например «АБ 1234567»'
    }
    case 'account_number':
    case 'correspondent_account':
    case 'bank_account': {
      const digits = digitsOnly(value)
      const label =
        key === 'correspondent_account'
          ? 'Корр. счёт'
          : key === 'bank_account'
            ? 'Банковский счёт'
            : 'Номер счёта'
      if (!strict && digits.length < 20) {
        if (/\D/.test(value.replace(/\s/g, ''))) return `${label}: только цифры`
        return null
      }
      if (digits.length !== 20) return `${label}: ожидается 20 цифр`
      return null
    }
    case 'bik': {
      const digits = digitsOnly(value)
      if (!strict && digits.length < 9) {
        if (/\D/.test(value)) return 'Только цифры'
        return null
      }
      if (digits.length !== 9) return 'Ожидается 9 цифр'
      return null
    }
    case 'kpp': {
      const digits = digitsOnly(value)
      if (!strict && digits.length < 9) {
        if (/\D/.test(value)) return 'Только цифры'
        return null
      }
      if (digits.length !== 9) return 'Ожидается 9 цифр'
      return null
    }
    case 'bank_receiver': {
      if (!strict && value.length < 3) return null
      if (value.length < 3) return 'Слишком короткое название'
      if (value.length > 200) return 'Слишком длинное название'
      return null
    }
    default:
      return null
  }
}

export function validateAllPrivateFields(
  data: Partial<Record<PrivateFieldKey, string | null | undefined>>,
): Partial<Record<PrivateFieldKey, string>> {
  const errors: Partial<Record<PrivateFieldKey, string>> = {}
  ;(Object.keys(data) as PrivateFieldKey[]).forEach((key) => {
    const msg = validatePrivateField(key, data[key], { strict: true })
    if (msg) errors[key] = msg
  })
  return errors
}
