import { useEffect, useState } from 'react'
import { adminApi, dictionariesApi } from '../api/endpoints'
import { StatusBadge } from '../components/StatusBadge'
import { errorMessage, formatDateTime, roleLabel } from '../lib/format'
import type { AuditLog, DictionaryItem, UserRead } from '../types/api'

const tabs = ['Пользователи', 'Справочники', 'Аудит'] as const

export function AdminPage() {
  const [tab, setTab] = useState<(typeof tabs)[number]>('Пользователи')
  const [users, setUsers] = useState<UserRead[]>([])
  const [departments, setDepartments] = useState<DictionaryItem[]>([])
  const [positions, setPositions] = useState<DictionaryItem[]>([])
  const [types, setTypes] = useState<DictionaryItem[]>([])
  const [statuses, setStatuses] = useState<DictionaryItem[]>([])
  const [audit, setAudit] = useState<AuditLog[]>([])
  const [error, setError] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editDept, setEditDept] = useState<number | ''>('')
  const [editPos, setEditPos] = useState<number | ''>('')

  async function loadUsers() {
    setUsers(await adminApi.users())
  }

  useEffect(() => {
    Promise.all([
      loadUsers(),
      dictionariesApi.departments().then(setDepartments),
      dictionariesApi.positions().then(setPositions),
      dictionariesApi.requestTypes().then(setTypes),
      dictionariesApi.statuses().then(setStatuses),
      adminApi.audit().then(setAudit),
    ]).catch((err) => setError(errorMessage(err)))
  }, [])

  async function toggleBlock(user: UserRead) {
    setError('')
    try {
      await adminApi.updateUser(user.id, {
        is_blocked: !user.is_blocked,
        block_reason: user.is_blocked ? undefined : 'Блокировка администратором',
      })
      await loadUsers()
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  function startEdit(user: UserRead) {
    setEditingId(user.id)
    setEditDept(user.department_id ?? '')
    setEditPos(user.position_id ?? '')
  }

  async function saveEdit(userId: number) {
    setError('')
    try {
      await adminApi.updateUser(userId, {
        department_id: editDept === '' ? null : editDept,
        position_id: editPos === '' ? null : editPos,
      })
      setEditingId(null)
      await loadUsers()
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Админ</h1>
      </div>

      <div className="tabs">
        {tabs.map((item) => (
          <button key={item} className={tab === item ? 'tab active' : 'tab'} onClick={() => setTab(item)}>
            {item}
          </button>
        ))}
      </div>

      {error && <p className="form-error">{error}</p>}

      {tab === 'Пользователи' && (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>ФИО</th>
                <th>Email</th>
                <th>Отдел</th>
                <th>Роль</th>
                <th>Статус</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td style={{ fontWeight: 500 }}>{user.full_name}</td>
                  <td>{user.email}</td>
                  <td>
                    {editingId === user.id ? (
                      <select value={editDept} onChange={(e) => setEditDept(e.target.value ? Number(e.target.value) : '')}>
                        <option value="">—</option>
                        {departments.map((item) => (
                          <option key={item.id} value={item.id}>
                            {item.name}
                          </option>
                        ))}
                      </select>
                    ) : (
                      user.department?.name ?? '—'
                    )}
                  </td>
                  <td>
                    {editingId === user.id ? (
                      <select value={editPos} onChange={(e) => setEditPos(e.target.value ? Number(e.target.value) : '')}>
                        <option value="">—</option>
                        {positions.map((item) => (
                          <option key={item.id} value={item.id}>
                            {item.name}
                          </option>
                        ))}
                      </select>
                    ) : (
                      roleLabel(user.role)
                    )}
                  </td>
                  <td>
                    <StatusBadge status={user.is_blocked ? 'Заблокирован' : 'Активен'} />
                  </td>
                  <td>
                    <div className="actions">
                      {editingId === user.id ? (
                        <>
                          <button className="btn btn-primary btn-sm" type="button" onClick={() => void saveEdit(user.id)}>
                            Сохранить
                          </button>
                          <button className="btn btn-secondary btn-sm" type="button" onClick={() => setEditingId(null)}>
                            Отмена
                          </button>
                        </>
                      ) : (
                        <button className="btn btn-secondary btn-sm" type="button" onClick={() => startEdit(user)}>
                          Изменить
                        </button>
                      )}
                      <button
                        className={user.is_blocked ? 'btn btn-primary btn-sm' : 'btn btn-danger btn-sm'}
                        type="button"
                        onClick={() => void toggleBlock(user)}
                      >
                        {user.is_blocked ? 'Разблок.' : 'Блок.'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'Справочники' && (
        <div className="grid-2">
          <DictCard title="Отделы" items={departments} />
          <DictCard title="Должности" items={positions} />
          <DictCard title="Типы заявок" items={types} />
          <DictCard title="Статусы" items={statuses} />
        </div>
      )}

      {tab === 'Аудит' && (
        <div className="card">
          <h3 className="section-title">Журнал изменений</h3>
          {audit.length === 0 && <p className="empty">Записей нет</p>}
          {audit.length > 0 && (
            <table className="table">
              <thead>
                <tr>
                  <th>Когда</th>
                  <th>Сущность</th>
                  <th>Действие</th>
                  <th>Кто</th>
                </tr>
              </thead>
              <tbody>
                {audit.map((row) => (
                  <tr key={row.id}>
                    <td>{formatDateTime(row.created_at)}</td>
                    <td>
                      {row.entity_name} #{row.entity_id}
                    </td>
                    <td>{row.action}</td>
                    <td>{row.user_id ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </>
  )
}

function DictCard({ title, items }: { title: string; items: DictionaryItem[] }) {
  return (
    <div className="card">
      <h3 className="section-title">{title}</h3>
      {items.length === 0 && <p className="empty">Пусто</p>}
      {items.map((item) => (
        <p className="muted" key={item.id} style={{ margin: '6px 0' }}>
          {item.name}
        </p>
      ))}
    </div>
  )
}
