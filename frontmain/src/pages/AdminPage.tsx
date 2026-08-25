import { useState } from 'react'
import { adminUsers } from '../data/mock'
import { StatusBadge } from '../components/StatusBadge'

const tabs = ['Пользователи', 'Справочники', 'Аудит'] as const

export function AdminPage() {
  const [tab, setTab] = useState<(typeof tabs)[number]>('Пользователи')

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Админ — Пользователи</h1>
        <button className="btn btn-primary" type="button">
          Добавить пользователя
        </button>
      </div>

      <div className="tabs">
        {tabs.map((t) => (
          <button key={t} className={tab === t ? 'tab active' : 'tab'} onClick={() => setTab(t)}>
            {t}
          </button>
        ))}
      </div>

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
              {adminUsers.map((user) => (
                <tr key={user.email}>
                  <td style={{ fontWeight: 500 }}>{user.name}</td>
                  <td>{user.email}</td>
                  <td>{user.dept}</td>
                  <td>{user.role}</td>
                  <td>
                    <StatusBadge status={user.blocked ? 'Заблокирован' : 'Активен'} />
                  </td>
                  <td>
                    <div className="actions">
                      <button className="btn btn-secondary btn-sm" type="button">
                        Изменить
                      </button>
                      <button
                        className={user.blocked ? 'btn btn-primary btn-sm' : 'btn btn-danger btn-sm'}
                        type="button"
                      >
                        {user.blocked ? 'Разблок.' : 'Блок.'}
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
        <div className="card">
          <h3 className="section-title">Справочники</h3>
          <p className="muted">· Отделы</p>
          <p className="muted">· Должности</p>
          <p className="muted">· Типы заявок</p>
          <p className="muted">· Статусы</p>
        </div>
      )}

      {tab === 'Аудит' && (
        <div className="card">
          <h3 className="section-title">Последний аудит</h3>
          <p className="muted">вход ivanov@… · 22.08 05:12</p>
          <p className="muted">смена статуса заявки #124</p>
          <p className="muted">просмотр ПДн</p>
          <p className="muted">генерация PDF</p>
        </div>
      )}
    </>
  )
}
