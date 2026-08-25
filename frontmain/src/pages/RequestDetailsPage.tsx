import { Link, useParams } from 'react-router-dom'
import { requests } from '../data/mock'
import { StatusBadge } from '../components/StatusBadge'

export function RequestDetailsPage() {
  const { id } = useParams()
  const item = requests.find((r) => String(r.id) === id) ?? requests[0]

  const steps = [
    { title: 'Создано', date: '05.03.2026, 10:24', done: true },
    { title: 'На согласовании', date: '05.03.2026, 10:25', done: true },
    { title: 'Одобрено руководителем', date: '—', done: false },
    { title: 'Документ сформирован', date: '—', done: false },
  ]

  return (
    <>
      <Link to="/requests" className="back-link">
        ← Назад к заявкам
      </Link>

      <div className="page-header">
        <div>
          <h1 className="page-title" style={{ fontSize: 22 }}>
            Заявка на {item.type.toLowerCase()} №{item.id}
          </h1>
          <p className="muted" style={{ margin: '6px 0 0' }}>
            Подана {item.date}
          </p>
        </div>
        <StatusBadge status={item.status} />
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 className="section-title">Статус</h3>
          <ul className="timeline">
            {steps.map((step) => (
              <li key={step.title}>
                <span className={step.done ? 'dot done' : 'dot'} />
                <div>
                  <div style={{ fontWeight: step.done ? 500 : 400, color: step.done ? 'var(--text)' : 'var(--muted)' }}>
                    {step.title}
                  </div>
                  <div className="muted" style={{ fontSize: 12 }}>
                    {step.date}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="card">
          <h3 className="section-title">Данные заявки</h3>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0' }}>
            <span className="muted">Тип</span>
            <span style={{ fontWeight: 500 }}>{item.type}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0' }}>
            <span className="muted">Период</span>
            <span style={{ fontWeight: 500 }}>{item.period}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0' }}>
            <span className="muted">Комментарий</span>
            <span style={{ fontWeight: 500 }}>{item.comment ?? '—'}</span>
          </div>
        </div>
      </div>
    </>
  )
}
