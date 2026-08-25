import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { adminApi, dictionariesApi, requestsApi } from '../api/endpoints'
import { StatusBadge } from '../components/StatusBadge'
import { useAuth } from '../auth/AuthContext'
import { errorMessage, formatDate, roleLabel } from '../lib/format'
import { hasPermission } from '../lib/permissions'
import { actionsForRequest, statusIdByName } from '../lib/requestActions'
import type { DictionaryItem, RequestRead, RequestStats, UserRead } from '../types/api'

export function HrPanelPage() {
  const { user, role } = useAuth()
  const [stats, setStats] = useState<RequestStats | null>(null)
  const [requests, setRequests] = useState<RequestRead[]>([])
  const [employees, setEmployees] = useState<UserRead[]>([])
  const [statuses, setStatuses] = useState<DictionaryItem[]>([])
  const [error, setError] = useState('')
  const [pendingId, setPendingId] = useState<number | null>(null)

  const canUsers = hasPermission(user, 'users:read_any')

  async function load() {
    const [statusList, statsData, list] = await Promise.all([
      dictionariesApi.statuses(),
      requestsApi.stats(),
      requestsApi.list(),
    ])
    setStatuses(statusList)
    setStats(statsData)
    setRequests(list)
    if (canUsers) setEmployees(await adminApi.users())
  }

  useEffect(() => {
    load().catch((err) => setError(errorMessage(err)))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canUsers])

  async function runAction(request: RequestRead, statusName: string) {
    const statusId = statusIdByName(statuses, statusName)
    if (!statusId) return
    setPendingId(request.id)
    setError('')
    try {
      await requestsApi.update(request.id, { status_id: statusId })
      await load()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPendingId(null)
    }
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">{role === 'manager' ? 'Согласование' : 'HR — Панель'}</h1>
        <div className="muted">
          {user?.full_name} · {roleLabel(role)}
        </div>
      </div>

      {error && <p className="form-error">{error}</p>}

      {stats && (
        <div className="grid-4">
          {[
            [String(stats.created), 'Созданы'],
            [String(stats.in_review), 'На проверке'],
            [String(stats.in_approval), 'На согласовании'],
            [String(stats.approved + stats.closed), 'Одобрены / закрыты'],
          ].map(([value, label]) => (
            <div className="card" key={label}>
              <p className="stat-value">{value}</p>
              <p className="stat-label">{label}</p>
            </div>
          ))}
        </div>
      )}

      <div className="card" style={{ marginTop: 16 }}>
        <h3 className="section-title">Очередь заявок</h3>
        {requests.length === 0 && <p className="empty">Заявок нет</p>}
        {requests.length > 0 && (
          <table className="table">
            <thead>
              <tr>
                <th>Сотрудник</th>
                <th>Тип</th>
                <th>Дата</th>
                <th>Согласующий</th>
                <th>Статус</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((row) => {
                const actions = actionsForRequest(row, role)
                return (
                  <tr key={row.id}>
                    <td style={{ fontWeight: 500 }}>
                      <Link to={`/requests/${row.id}`} style={{ color: 'var(--primary)' }}>
                        {row.employee?.full_name ?? '—'}
                      </Link>
                    </td>
                    <td>{row.request_type.name}</td>
                    <td>{formatDate(row.created_at)}</td>
                    <td>{row.approver?.full_name ?? '—'}</td>
                    <td>
                      <StatusBadge status={row.status.name} />
                    </td>
                    <td>
                      <div className="actions">
                        {actions.map((action) => (
                          <button
                            key={action.statusName}
                            className={
                              action.kind === 'danger'
                                ? 'btn btn-danger btn-sm'
                                : action.kind === 'secondary'
                                  ? 'btn btn-secondary btn-sm'
                                  : 'btn btn-primary btn-sm'
                            }
                            type="button"
                            disabled={pendingId === row.id}
                            onClick={() => void runAction(row, action.statusName)}
                          >
                            {action.label}
                          </button>
                        ))}
                        {actions.length === 0 && <span className="muted">—</span>}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {canUsers && (
        <div className="card" style={{ marginTop: 16 }}>
          <div className="page-header" style={{ marginBottom: 8 }}>
            <h3 className="section-title" style={{ margin: 0 }}>
              Сотрудники
            </h3>
            <span className="muted">Просмотр карточки. Смена отдела и должности — только у администратора</span>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>ФИО</th>
                <th>Отдел</th>
                <th>Должность</th>
                <th>Email</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {employees.map((emp) => (
                <tr key={emp.id}>
                  <td style={{ fontWeight: 500 }}>{emp.full_name}</td>
                  <td>{emp.department?.name ?? '—'}</td>
                  <td>{emp.position?.name ?? '—'}</td>
                  <td>{emp.email}</td>
                  <td>
                    <Link to={`/hr/employees/${emp.id}`} className="btn btn-primary btn-sm">
                      Открыть
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
