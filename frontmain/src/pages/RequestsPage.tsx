import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { requests } from '../data/mock'
import { StatusBadge } from '../components/StatusBadge'

const filters = ['Все', 'На рассмотрении', 'Одобрено', 'Отклонено'] as const

export function RequestsPage() {
  const [filter, setFilter] = useState<(typeof filters)[number]>('Все')

  const list = useMemo(() => {
    if (filter === 'Все') return requests
    return requests.filter((r) => r.status === filter)
  }, [filter])

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Мои заявки</h1>
        <Link to="/requests/new" className="btn btn-primary">
          Новая заявка
        </Link>
      </div>

      <div className="tabs">
        {filters.map((f) => (
          <button
            key={f}
            className={filter === f ? 'tab active' : 'tab'}
            onClick={() => setFilter(f)}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="card">
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
            {list.map((item) => (
              <tr key={item.id}>
                <td>
                  <Link to={`/requests/${item.id}`} style={{ fontWeight: 500, color: 'var(--primary)' }}>
                    {item.type}
                  </Link>
                </td>
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
