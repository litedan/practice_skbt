import { Link } from 'react-router-dom'
import { currentUser, notifications, requests } from '../data/mock'
import { StatusBadge } from '../components/StatusBadge'

export function HomePage() {
  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Главная</h1>
        <div className="muted">
          Уведомления · {notifications.length} · {currentUser.name}
        </div>
      </div>

      <p style={{ marginTop: 0, fontWeight: 600, fontSize: 18 }}>Добро пожаловать, Иван!</p>
      <p className="muted" style={{ marginTop: 4 }}>
        Быстрый доступ к заявкам и документам
      </p>

      <div className="grid-3" style={{ marginTop: 24 }}>
        <Link to="/requests/new" className="quick-card primary">
          <div style={{ fontWeight: 600 }}>Подать заявку</div>
          <div className="muted" style={{ marginTop: 6 }}>
            Отпуск или больничный
          </div>
        </Link>
        <Link to="/requests/new" className="quick-card">
          <div style={{ fontWeight: 600 }}>Заказать справку</div>
          <div className="muted" style={{ marginTop: 6 }}>
            2-НДФЛ, с места работы
          </div>
        </Link>
        <Link to="/documents" className="quick-card">
          <div style={{ fontWeight: 600 }}>Подписать документ</div>
          <div className="muted" style={{ marginTop: 6 }}>
            1 документ ожидает
          </div>
        </Link>
      </div>

      <div className="grid-2" style={{ marginTop: 16 }}>
        <div className="card">
          <p className="muted" style={{ margin: 0 }}>
            Остаток отпуска
          </p>
          <p className="stat-value">{currentUser.vacationDays} дней</p>
          <p className="stat-label">Ежегодный оплачиваемый</p>
        </div>
        <div className="card">
          <h3 className="section-title">Уведомления</h3>
          {notifications.map((text) => (
            <div key={text} style={{ display: 'flex', gap: 10, alignItems: 'center', padding: '6px 0' }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--primary)' }} />
              <span style={{ fontSize: 13 }}>{text}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <div className="page-header" style={{ marginBottom: 8 }}>
          <h3 className="section-title" style={{ margin: 0 }}>
            Последние заявки
          </h3>
          <Link to="/requests" className="link">
            Все заявки
          </Link>
        </div>
        <table className="table">
          <thead>
            <tr>
              <th>Тип</th>
              <th>Период</th>
              <th>Дата</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            {requests.slice(0, 3).map((item) => (
              <tr key={item.id}>
                <td style={{ fontWeight: 500 }}>{item.type}</td>
                <td>{item.period}</td>
                <td>{item.date}</td>
                <td>
                  <StatusBadge status={item.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
