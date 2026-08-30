import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { useAuth } from '../auth/AuthContext'
import { usersApi } from '../api/endpoints'
import { StatusBadge } from '../components/StatusBadge'
import { errorMessage, formatDate, roleLabel } from '../lib/format'
import { hasPermission } from '../lib/permissions'
import {
  validateAllPrivateFields,
  validatePrivateField,
  type PrivateFieldKey,
} from '../lib/privateDataValidation'
import type { UserPrivateData } from '../types/api'

const PRIVATE_KEYS: PrivateFieldKey[] = [
  'passport',
  'military_id',
  'inn',
  'snils',
  'account_number',
  'correspondent_account',
  'bik',
  'kpp',
  'bank_receiver',
  'bank_account',
]

export function ProfilePage() {
  const { user, refreshUser } = useAuth()
  const [phone, setPhone] = useState(user?.phone ?? '')
  const [city, setCity] = useState(user?.city ?? '')
  const [privateData, setPrivateData] = useState<UserPrivateData | null>(null)
  const [canPrivate, setCanPrivate] = useState(false)
  const [fieldErrors, setFieldErrors] = useState<Partial<Record<PrivateFieldKey, string>>>({})
  const [touched, setTouched] = useState<Partial<Record<PrivateFieldKey, boolean>>>({})
  const [error, setError] = useState('')
  const [ok, setOk] = useState('')
  const [pending, setPending] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')

  useEffect(() => {
    setPhone(user?.phone ?? '')
    setCity(user?.city ?? '')
  }, [user])

  useEffect(() => {
    if (!user) return
    if (!hasPermission(user, 'private_data:read_self', 'private_data:read_any')) return
    usersApi
      .getPrivate(user.id)
      .then((data) => {
        setPrivateData(data)
        setCanPrivate(true)
        setFieldErrors({})
        setTouched({})
      })
      .catch(() => setCanPrivate(false))
  }, [user])

  const hasBlockingErrors = useMemo(
    () => Object.values(fieldErrors).some(Boolean),
    [fieldErrors],
  )

  function setPrivateField(key: PrivateFieldKey, value: string) {
    if (!privateData) return
    setPrivateData({ ...privateData, [key]: value })
    const msg = validatePrivateField(key, value, { strict: Boolean(touched[key]) })
    setFieldErrors((prev) => {
      const next = { ...prev }
      if (msg) next[key] = msg
      else delete next[key]
      return next
    })
  }

  function touchField(key: PrivateFieldKey) {
    setTouched((prev) => ({ ...prev, [key]: true }))
    if (!privateData) return
    const msg = validatePrivateField(key, privateData[key], { strict: true })
    setFieldErrors((prev) => {
      const next = { ...prev }
      if (msg) next[key] = msg
      else delete next[key]
      return next
    })
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (!user) return
    setError('')
    setOk('')

    if (canPrivate && privateData) {
      const payload = Object.fromEntries(
        PRIVATE_KEYS.map((key) => [key, privateData[key]]),
      ) as Partial<Record<PrivateFieldKey, string | null | undefined>>
      const errors = validateAllPrivateFields(payload)
      setTouched(Object.fromEntries(PRIVATE_KEYS.map((k) => [k, true])))
      setFieldErrors(errors)
      if (Object.keys(errors).length > 0) {
        setError('Исправьте ошибки в полях перед сохранением')
        return
      }
    }

    setPending(true)
    try {
      await usersApi.updateMe({ phone: phone.trim() || null, city: city.trim() || null })
      if (canPrivate && privateData) {
        await usersApi.updatePrivate(user.id, {
          passport: privateData.passport,
          inn: privateData.inn,
          snils: privateData.snils,
          military_id: privateData.military_id,
          contract_number: privateData.contract_number,
          account_number: privateData.account_number,
          correspondent_account: privateData.correspondent_account,
          bik: privateData.bik,
          kpp: privateData.kpp,
          bank_receiver: privateData.bank_receiver,
          bank_account: privateData.bank_account,
        })
      }
      await refreshUser()
      setOk('Сохранено')
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPending(false)
    }
  }

  async function onChangePassword(e: FormEvent) {
    e.preventDefault()
    setError('')
    setOk('')
    setPending(true)
    try {
      await usersApi.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      })
      setOk('Пароль изменён')
      setCurrentPassword('')
      setNewPassword('')
      setShowPassword(false)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPending(false)
    }
  }

  if (!user) return null

  return (
    <>
      <h1 className="page-title">Профиль</h1>
      {error && <p className="form-error">{error}</p>}
      {ok && <p className="form-ok">{ok}</p>}

      <form onSubmit={(e) => void onSubmit(e)} noValidate>
        <div className="card" style={{ marginTop: 24 }}>
          <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
            <div
              style={{
                width: 64,
                height: 64,
                borderRadius: '50%',
                background: '#d9e6ff',
                flexShrink: 0,
              }}
            />
            <div>
              <div style={{ fontWeight: 600, fontSize: 18 }}>{user.full_name}</div>
              <div className="muted">
                {roleLabel(user.role)}
                {user.position ? ` · ${user.position.name}` : ''}
                {user.department ? ` · ${user.department.name}` : ''}
              </div>
              <div className="muted">Принят: {formatDate(user.hire_date)}</div>
            </div>
          </div>

          <div className="grid-2" style={{ marginTop: 24 }}>
            <div className="field">
              <label>Email</label>
              <input value={user.email ?? ''} disabled />
            </div>
            <div className="field">
              <label>Отдел</label>
              <input value={user.department?.name ?? '—'} disabled />
            </div>
            <div className="field">
              <label>Телефон</label>
              <input value={phone} onChange={(e) => setPhone(e.target.value)} />
            </div>
            <div className="field">
              <label>Должность</label>
              <input value={user.position?.name ?? '—'} disabled />
            </div>
            <div className="field">
              <label>Дата рождения</label>
              <input value={formatDate(user.birth_date)} disabled />
            </div>
            <div className="field">
              <label>Город</label>
              <input value={city} onChange={(e) => setCity(e.target.value)} />
            </div>
          </div>
        </div>

        {canPrivate && privateData && (
          <>
            <div className="card">
              <h3 className="section-title">Персональные данные</h3>
              <div className="grid-2">
                <Field
                  label="Паспорт"
                  fieldKey="passport"
                  value={privateData.passport ?? ''}
                  placeholder="4510 123456"
                  error={fieldErrors.passport}
                  onChange={setPrivateField}
                  onBlur={touchField}
                />
                <Field
                  label="Военный билет"
                  fieldKey="military_id"
                  value={privateData.military_id ?? ''}
                  placeholder="АБ 1234567"
                  error={fieldErrors.military_id}
                  onChange={setPrivateField}
                  onBlur={touchField}
                />
                <Field
                  label="ИНН"
                  fieldKey="inn"
                  value={privateData.inn ?? ''}
                  placeholder="12 цифр"
                  error={fieldErrors.inn}
                  onChange={setPrivateField}
                  type="number"
                  onBlur={touchField}
                />
                <Field
                  label="СНИЛС"
                  fieldKey="snils"
                  value={privateData.snils ?? ''}
                  placeholder="123-456-789 01"
                  error={fieldErrors.snils}
                  onChange={setPrivateField}
                  onBlur={touchField}
                />
                <div className="field">
                  <label>Номер договора</label>
                  <input value={privateData.contract_number ?? ''} disabled />
                </div>
              </div>
            </div>

            <ConsentBlock userId={user.id} />

            <div className="card">
              <h3 className="section-title">Банковские реквизиты</h3>
              <div className="grid-2">
                <Field
                  label="Номер счёта"
                  fieldKey="account_number"
                  value={privateData.account_number ?? ''}
                  placeholder="20 цифр"
                  type="number"
                  error={fieldErrors.account_number}
                  onChange={setPrivateField}
                  onBlur={touchField}
                />
                <Field
                  label="Корр. счёт"
                  fieldKey="correspondent_account"
                  value={privateData.correspondent_account ?? ''}
                  placeholder="20 цифр"
                  type="number"
                  error={fieldErrors.correspondent_account}
                  onChange={setPrivateField}
                  onBlur={touchField}
                />
                <Field
                  label="БИК"
                  fieldKey="bik"
                  value={privateData.bik ?? ''}
                  placeholder="9 цифр"
                  type="number"
                  error={fieldErrors.bik}
                  onChange={setPrivateField}
                  onBlur={touchField}
                />
                <Field
                  label="КПП"
                  fieldKey="kpp"
                  value={privateData.kpp ?? ''}
                  placeholder="9 цифр"
                  type="number"
                  error={fieldErrors.kpp}
                  onChange={setPrivateField}
                  onBlur={touchField}
                />
                <Field
                  label="Банк получатель"
                  fieldKey="bank_receiver"
                  value={privateData.bank_receiver ?? ''}
                  placeholder="ПАО Сбербанк"
                  error={fieldErrors.bank_receiver}
                  onChange={setPrivateField}
                  onBlur={touchField}
                />
              </div>
            </div>
          </>
        )}

        {!canPrivate && <ConsentBlock userId={user.id} />}

        <div className="actions" style={{ marginTop: 8 }}>
          <button
            className="btn btn-primary"
            type="submit"
            disabled={pending || hasBlockingErrors}
          >
            Сохранить
          </button>
          <button className="btn btn-secondary" type="button" onClick={() => setShowPassword((v) => !v)}>
            Сменить пароль
          </button>
        </div>
      </form>

      {showPassword && (
        <form className="card" onSubmit={(e) => void onChangePassword(e)}>
          <h3 className="section-title">Смена пароля</h3>
          <div className="grid-2">
            <div className="field">
              <label>Текущий пароль</label>
              <input
                type="password"
                value={currentPassword}
                minLength={8}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label>Новый пароль</label>
              <input
                type="password"
                value={newPassword}
                minLength={8}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
            </div>
          </div>
          <button className="btn btn-primary" type="submit" disabled={pending}>
            Обновить пароль
          </button>
        </form>
      )}
    </>
  )
}

function Field({
  label,
  fieldKey,
  value,
  onChange,
  onBlur,
  placeholder,
  error,
  type='text',
}: {
  label: string
  fieldKey: PrivateFieldKey
  value: string
  onChange: (key: PrivateFieldKey, value: string) => void
  onBlur: (key: PrivateFieldKey) => void
  placeholder?: string
  error?: string
  type?: string
}) {
  return (
    <div className="field">
      <label htmlFor={`pd-${fieldKey}`}>{label}</label>
      <input
        id={`pd-${fieldKey}`}
        value={value}
        placeholder={placeholder}
        type={type}
        className={error ? 'invalid' : undefined}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `pd-${fieldKey}-error` : undefined}
        onChange={(e) => onChange(fieldKey, e.target.value)}
        onBlur={() => onBlur(fieldKey)}
      />
      {error && (
        <p className="field-error" id={`pd-${fieldKey}-error`}>
          {error}
        </p>
      )}
    </div>
  )
}

type ConsentState = {
  status: 'Действует' | 'Не подписано' | 'Отозван'
  signedAt: string | null
}

function consentKey(userId: number) {
  return `kedo_consent_${userId}`
}

function loadConsent(userId: number): ConsentState {
  try {
    const raw = localStorage.getItem(consentKey(userId))
    if (!raw) return { status: 'Не подписано', signedAt: null }
    return JSON.parse(raw) as ConsentState
  } catch {
    return { status: 'Не подписано', signedAt: null }
  }
}

function ConsentBlock({ userId }: { userId: number }) {
  const [consent, setConsent] = useState<ConsentState>(() => loadConsent(userId))

  useEffect(() => {
    setConsent(loadConsent(userId))
  }, [userId])

  function persist(next: ConsentState) {
    setConsent(next)
    localStorage.setItem(consentKey(userId), JSON.stringify(next))
  }

  return (
    <div className="card">
      <h3 className="section-title">Согласие на обработку персональных данных</h3>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
        <div>
          <div style={{ fontWeight: 500 }}>Цель: кадровый учёт и документооборот</div>
          <div className="muted" style={{ marginTop: 4 }}>
            {consent.signedAt ? `Подписано: ${formatDate(consent.signedAt)}` : 'Ещё не подписано'}
          </div>
        </div>
        <StatusBadge status={consent.status} />
      </div>
      <div className="actions" style={{ marginTop: 16 }}>
        {consent.status !== 'Действует' && (
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={() =>
              persist({ status: 'Действует', signedAt: new Date().toISOString() })
            }
          >
            Подписать согласие
          </button>
        )}
        {consent.status === 'Действует' && (
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => persist({ status: 'Отозван', signedAt: consent.signedAt })}
          >
            Отозвать
          </button>
        )}
      </div>
    </div>
  )
}
