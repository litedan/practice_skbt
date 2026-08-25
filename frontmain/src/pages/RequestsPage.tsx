import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { dictionariesApi, requestsApi } from '../api/endpoints'
import { StatusBadge } from '../components/StatusBadge'
import { useAuth } from '../auth/AuthContext'
import { formatDate } from '../lib/format'
import { hasPermission } from '../lib/permissions'
import type { DictionaryItem, RequestRead } from '../types/api'

export function RequestsPage() {
  const { user } = useAuth()
  const [filterId, setFilterId] = useState<number | 'all'>('all')
  const [statuses, setStatuses] = useState<DictionaryItem[]>([])
  const [list, setList] = useState<RequestRead[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const canCreate = hasPermission(user, 'requests:create')
  const title = hasPermission(user, 'requests:read_any')
    ? 'Заявки'
    : hasPermission(user, 'requests:read_department')
      ? 'Заявки отдела'
      : 'Мои заявки'

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError('')
      try {
        const [statusList, requests] = await Promise.all([
          dictionariesApi.statuses(),
          requestsApi.list(filterId === 'all' ? undefined : { status_id: filterId }),
        ])
        if (cancelled) return
        setStatuses(statusList)
        setList(requests)
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Ошибка загрузки')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [filterId])

  const filters = useMemo(() => [{ id: 'all' as const, name: 'Все' }, ...statuses], [statuses])

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">{title}</h1>
        {canCreate && (
          <Link to="/requests/new" className="btn btn-primary">
            Новая заявка
          </Link>
        )}
      </div>

      <div className="tabs">
        {filters.map((item) => (
          <button
            key={item.id}
            className={filterId === item.id ? 'tab active' : 'tab'}
            onClick={() => setFilterId(item.id)}
          >
            {item.name}
          </button>
        ))}
      </div>

      {error && <p className="form-error">{error}</p>}

      <div className="card">
        {loading && <p className="empty">Загрузка…</p>}
        {!loading && list.length === 0 && <p className="empty">Заявок нет</p>}
        {!loading && list.length > 0 && (
          <table className="table">
            <thead>
              <tr>
                <th>Тип</th>
                <th>Сотрудник</th>
                <th>Дата</th>
                <th>Статус</th>
              </tr>
            </thead>
            <tbody>
              {list.map((item) => (
                <tr key={item.id}>
                  <td>
                    <Link to={`/requests/${item.id}`} style={{ fontWeight: 500, color: 'var(--primary)' }}>
                      {item.request_type.name} #{item.id}
                    </Link>
                  </td>
                  <td>{item.employee?.full_name ?? '—'}</td>
                  <td>{formatDate(item.created_at)}</td>
                  <td>
                    <StatusBadge status={item.status.name} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  )
}
