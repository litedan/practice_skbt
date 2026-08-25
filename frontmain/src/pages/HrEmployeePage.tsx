import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { usersApi } from '../api/endpoints'
import { errorMessage, formatDate } from '../lib/format'
import type { UserPrivateData, UserRead } from '../types/api'

export function HrEmployeePage() {
  const { id } = useParams()
  const userId = Number(id)
  const [emp, setEmp] = useState<UserRead | null>(null)
  const [privateData, setPrivateData] = useState<UserPrivateData | null>(null)
  const [error, setError] = useState('')
  const [loadingPrivate, setLoadingPrivate] = useState(false)

  useEffect(() => {
    if (!Number.isFinite(userId)) return
    usersApi
      .get(userId)
      .then(setEmp)
      .catch((err) => setError(errorMessage(err)))
  }, [userId])

  async function showPrivate() {
    setLoadingPrivate(true)
    setError('')
    try {
      setPrivateData(await usersApi.getPrivate(userId))
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoadingPrivate(false)
    }
  }

  if (error && !emp) return <p className="form-error">{error}</p>
  if (!emp) return <p className="empty">Загрузка…</p>

  return (
    <>
      <Link to="/hr" className="back-link">
        ← Назад к панели
      </Link>

      <div className="page-header">
        <div>
          <h1 className="page-title" style={{ fontSize: 22 }}>
            Карточка сотрудника
          </h1>
          <p className="muted" style={{ margin: '6px 0 0' }}>
            {emp.full_name} · id {emp.id}
          </p>
        </div>
      </div>

      {error && <p className="form-error">{error}</p>}

      <div className="card">
        <div className="grid-2">
          <div className="field">
            <label>ФИО</label>
            <input value={emp.full_name} disabled />
          </div>
          <div className="field">
            <label>Отдел</label>
            <input value={emp.department?.name ?? '—'} disabled />
          </div>
          <div className="field">
            <label>Email</label>
            <input value={emp.email ?? ''} disabled />
          </div>
          <div className="field">
            <label>Должность</label>
            <input value={emp.position?.name ?? '—'} disabled />
          </div>
          <div className="field">
            <label>Телефон</label>
            <input value={emp.phone ?? '—'} disabled />
          </div>
          <div className="field">
            <label>Город</label>
            <input value={emp.city ?? '—'} disabled />
          </div>
          <div className="field">
            <label>Дата рождения</label>
            <input value={formatDate(emp.birth_date)} disabled />
          </div>
          <div className="field">
            <label>Дата поступления</label>
            <input value={formatDate(emp.hire_date)} disabled />
          </div>
        </div>

        <div className="actions" style={{ marginBottom: 0 }}>
          <button className="btn btn-secondary" type="button" onClick={() => void showPrivate()} disabled={loadingPrivate}>
            {loadingPrivate ? 'Загрузка…' : 'Показать ПДн'}
          </button>
          <span className="muted">Запрос пишется в лог</span>
        </div>
      </div>

      {privateData && (
        <div className="card">
          <h3 className="section-title">Персональные данные</h3>
          <div className="grid-2">
            <div className="field">
              <label>Паспорт</label>
              <input value={privateData.passport ?? '—'} disabled />
            </div>
            <div className="field">
              <label>ИНН</label>
              <input value={privateData.inn ?? '—'} disabled />
            </div>
            <div className="field">
              <label>СНИЛС</label>
              <input value={privateData.snils ?? '—'} disabled />
            </div>
            <div className="field">
              <label>Договор</label>
              <input value={privateData.contract_number ?? '—'} disabled />
            </div>
          </div>
        </div>
      )}
    </>
  )
}
