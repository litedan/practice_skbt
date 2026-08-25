import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { notificationsApi, requestsApi } from '../api/endpoints'
import { StatusBadge } from '../components/StatusBadge'
import { useAuth } from '../auth/AuthContext'
import { firstName, formatDate } from '../lib/format'
import { hasPermission } from '../lib/permissions'
import type { NotificationItem, RequestRead } from '../types/api'

export function HomePage() {
  const { user } = useAuth()
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [requests, setRequests] = useState<RequestRead[]>([])
  const [error, setError] = useState('')

  const canRequests = hasPermission(
    user,
    'requests:read_self',
    'requests:read_any',
    'requests:read_department',
  )
  const canNotify = hasPermission(user, 'notifications:read_self')
  const canCreate = hasPermission(user, 'requests:create')

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const [notes, list] = await Promise.all([
          canNotify ? notificationsApi.list() : Promise.resolve([]),
          canRequests ? requestsApi.list() : Promise.resolve([]),
        ])
        if (cancelled) return
        setNotifications(notes)
        setRequests(list)
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Ошибка загрузки')
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [canNotify, canRequests])

  const unread = notifications.filter((item) => !item.is_read)

  async function markRead(id: number) {
    await notificationsApi.markRead(id)
    setNotifications((prev) => prev.map((item) => (item.id === id ? { ...item, is_read: true } : item)))
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Главная</h1>
        {canNotify && (
          <div className="muted">
            Уведомления · {unread.length} непрочитанных
            {user ? ` · ${user.full_name}` : ''}
          </div>
        )}
      </div>

      <p style={{ marginTop: 0, fontWeight: 600, fontSize: 18 }}>
        Добро пожаловать{user ? `, ${firstName(user.full_name)}` : ''}!
      </p>
      <p className="muted" style={{ marginTop: 4 }}>
        {user?.position?.name}
        {user?.department ? ` · ${user.department.name}` : ''}
      </p>

      {error && <p className="form-error">{error}</p>}

      {canCreate && (
        <div className="grid-3" style={{ marginTop: 24 }}>
          <Link to="/requests/new" className="quick-card primary">
            <div style={{ fontWeight: 600 }}>Подать заявку</div>
            <div className="muted" style={{ marginTop: 6 }}>
              Тип и комментарий
            </div>
          </Link>
          <Link to="/requests" className="quick-card">
            <div style={{ fontWeight: 600 }}>Мои заявки</div>
            <div className="muted" style={{ marginTop: 6 }}>
              Статусы и вложения
            </div>
          </Link>
          <Link to="/profile" className="quick-card">
            <div style={{ fontWeight: 600 }}>Профиль</div>
            <div className="muted" style={{ marginTop: 6 }}>
              Контакты и персональные данные
            </div>
          </Link>
        </div>
      )}

      <div className="grid-2" style={{ marginTop: 16 }}>
        {canNotify && (
          <div className="card">
            <h3 className="section-title">Уведомления</h3>
            {notifications.length === 0 && <p className="empty">Пока нет уведомлений</p>}
            {notifications.slice(0, 8).map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => {
                  if (!item.is_read) void markRead(item.id)
                }}
                style={{
                  display: 'flex',
                  gap: 10,
                  alignItems: 'flex-start',
                  padding: '8px 0',
                  width: '100%',
                  textAlign: 'left',
                  background: 'none',
                  border: 'none',
                  cursor: item.is_read ? 'default' : 'pointer',
                }}
              >
                <span
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: '50%',
                    marginTop: 6,
                    background: item.is_read ? '#d1d5db' : 'var(--primary)',
                    flexShrink: 0,
                  }}
                />
                <span style={{ fontSize: 13 }}>
                  <strong>{item.title}</strong>
                  <br />
                  <span className="muted">{item.message}</span>
                </span>
              </button>
            ))}
          </div>
        )}

        {canRequests && (
          <div className="card">
            <div className="page-header" style={{ marginBottom: 8 }}>
              <h3 className="section-title" style={{ margin: 0 }}>
                Последние заявки
              </h3>
              <Link to="/requests" className="link">
                Все заявки
              </Link>
            </div>
            {requests.length === 0 && <p className="empty">Заявок нет</p>}
            <table className="table">
              <tbody>
                {requests.slice(0, 5).map((item) => (
                  <tr key={item.id}>
                    <td style={{ fontWeight: 500 }}>
                      <Link to={`/requests/${item.id}`} style={{ color: 'var(--primary)' }}>
                        {item.request_type.name}
                      </Link>
                    </td>
                    <td>{formatDate(item.created_at)}</td>
                    <td>
                      <StatusBadge status={item.status.name} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  )
}
