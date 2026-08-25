import { useEffect, useState, type FormEvent } from 'react'
import { useAuth } from '../auth/AuthContext'
import { usersApi } from '../api/endpoints'
import { errorMessage, formatDate, roleLabel } from '../lib/format'
import { hasPermission } from '../lib/permissions'
import type { UserPrivateData } from '../types/api'

export function ProfilePage() {
  const { user, refreshUser } = useAuth()
  const [phone, setPhone] = useState(user?.phone ?? '')
  const [city, setCity] = useState(user?.city ?? '')
  const [privateData, setPrivateData] = useState<UserPrivateData | null>(null)
  const [canPrivate, setCanPrivate] = useState(false)
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
      })
      .catch(() => setCanPrivate(false))
  }, [user])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (!user) return
    setError('')
    setOk('')
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

      <form onSubmit={(e) => void onSubmit(e)}>
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
              <p className="muted" style={{ marginTop: 0, color: 'var(--primary)' }}>
                Запросы пишутся в sensitive_access_log
              </p>
              <div className="grid-2">
                <Field
                  label="Паспорт"
                  value={privateData.passport ?? ''}
                  onChange={(v) => setPrivateData({ ...privateData, passport: v })}
                />
                <Field
                  label="Военный билет"
                  value={privateData.military_id ?? ''}
                  onChange={(v) => setPrivateData({ ...privateData, military_id: v })}
                />
                <Field
                  label="ИНН"
                  value={privateData.inn ?? ''}
                  onChange={(v) => setPrivateData({ ...privateData, inn: v })}
                />
                <Field
                  label="СНИЛС"
                  value={privateData.snils ?? ''}
                  onChange={(v) => setPrivateData({ ...privateData, snils: v })}
                />
                <div className="field">
                  <label>Номер договора</label>
                  <input value={privateData.contract_number ?? ''} disabled />
                </div>
              </div>
            </div>

            <div className="card">
              <h3 className="section-title">Банковские реквизиты</h3>
              <div className="grid-2">
                <Field
                  label="Номер счёта"
                  value={privateData.account_number ?? ''}
                  onChange={(v) => setPrivateData({ ...privateData, account_number: v })}
                />
                <Field
                  label="Корр. счёт"
                  value={privateData.correspondent_account ?? ''}
                  onChange={(v) => setPrivateData({ ...privateData, correspondent_account: v })}
                />
                <Field
                  label="БИК"
                  value={privateData.bik ?? ''}
                  onChange={(v) => setPrivateData({ ...privateData, bik: v })}
                />
                <Field
                  label="КПП"
                  value={privateData.kpp ?? ''}
                  onChange={(v) => setPrivateData({ ...privateData, kpp: v })}
                />
                <Field
                  label="Банк получатель"
                  value={privateData.bank_receiver ?? ''}
                  onChange={(v) => setPrivateData({ ...privateData, bank_receiver: v })}
                />
              </div>
            </div>
          </>
        )}

        <div className="actions" style={{ marginTop: 8 }}>
          <button className="btn btn-primary" type="submit" disabled={pending}>
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
  value,
  onChange,
}: {
  label: string
  value: string
  onChange: (value: string) => void
}) {
  return (
    <div className="field">
      <label>{label}</label>
      <input value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  )
}
