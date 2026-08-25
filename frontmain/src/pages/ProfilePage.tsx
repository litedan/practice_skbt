import { type FormEvent } from 'react'
import { currentUser as user } from '../data/mock'

export function ProfilePage() {
  function onSubmit(e: FormEvent) {
    e.preventDefault()
    alert('Сохранено (демо без backend)')
  }

  return (
    <>
      <h1 className="page-title">Профиль</h1>

      <form onSubmit={onSubmit}>
        {/* Шапка */}
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
              <div style={{ fontWeight: 600, fontSize: 18 }}>{user.fullName}</div>
              <div className="muted">{user.roleLabel}</div>
              <div className="muted">Принят: {user.hireDate}</div>
            </div>
          </div>

          <div className="grid-2" style={{ marginTop: 24 }}>
            <div className="field">
              <label>Email</label>
              <input defaultValue={user.email} disabled />
            </div>
            <div className="field">
              <label>Отдел</label>
              <input defaultValue={user.dept} disabled />
            </div>
            <div className="field">
              <label>Телефон</label>
              <input defaultValue={user.phone} />
            </div>
            <div className="field">
              <label>Должность</label>
              <input defaultValue={user.position} disabled />
            </div>
          </div>
        </div>

        {/* Личные данные */}
        <div className="card">
          <h3 className="section-title">Личные данные</h3>
          <div className="grid-2">
            <div className="field">
              <label>Дата рождения</label>
              <input defaultValue={user.birthDate} disabled />
            </div>
            <div className="field">
              <label>Город</label>
              <input defaultValue={user.city} />
            </div>
            <div className="field">
              <label>Дата поступления</label>
              <input defaultValue={user.hireDate} disabled />
            </div>
            <div className="field">
              <label>Номер договора</label>
              <input defaultValue={user.contractNumber} disabled />
            </div>
          </div>
        </div>

        {/* Персональные данные */}
        <div className="card">
          <h3 className="section-title">Персональные данные</h3>
          <p className="muted" style={{ marginTop: 0, color: 'var(--primary)' }}>
            Доступ логируется (sensitive_access_log)
          </p>
          <div className="grid-2">
            <div className="field">
              <label>Паспорт</label>
              <input defaultValue={user.passport} disabled />
            </div>
            <div className="field">
              <label>Адрес регистрации</label>
              <input defaultValue={user.address} />
            </div>
            <div className="field">
              <label>ИНН</label>
              <input defaultValue={user.inn} disabled />
            </div>
            <div className="field">
              <label>Военный билет</label>
              <input defaultValue={user.militaryId} disabled />
            </div>
            <div className="field">
              <label>СНИЛС</label>
              <input defaultValue={user.snils} disabled />
            </div>
          </div>
        </div>

        {/* Банк */}
        <div className="card">
          <h3 className="section-title">Банковские реквизиты</h3>
          <div className="grid-2">
            <div className="field">
              <label>Номер счёта</label>
              <input defaultValue={user.accountNumber} />
            </div>
            <div className="field">
              <label>Корр. счёт</label>
              <input defaultValue={user.corrAccount} />
            </div>
            <div className="field">
              <label>БИК</label>
              <input defaultValue={user.bik} />
            </div>
            <div className="field">
              <label>КПП</label>
              <input defaultValue={user.kpp} />
            </div>
            <div className="field">
              <label>Банк получатель</label>
              <input defaultValue={user.bankName} />
            </div>
          </div>
        </div>

        <div className="actions" style={{ marginTop: 8 }}>
          <button className="btn btn-primary" type="submit">
            Сохранить
          </button>
          <button className="btn btn-secondary" type="button">
            Сменить пароль
          </button>
        </div>
      </form>
    </>
  )
}
