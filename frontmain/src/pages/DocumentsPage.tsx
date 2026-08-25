import { useState } from 'react'
import { Link } from 'react-router-dom'
import { documents } from '../data/mock'
import { StatusBadge } from '../components/StatusBadge'

const filters = ['Все', 'На подпись', 'Подписанные'] as const

export function DocumentsPage() {
  const [filter, setFilter] = useState<(typeof filters)[number]>('Все')

  const list = documents.filter((doc) => {
    if (filter === 'Все') return true
    if (filter === 'На подпись') return Boolean(doc.needSign)
    return !doc.needSign
  })

  return (
    <>
      <h1 className="page-title">Документы</h1>

      <div className="tabs" style={{ marginTop: 20 }}>
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
              <th>Документ</th>
              <th>Дата</th>
              <th>Статус</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {list.map((doc) => (
              <tr key={doc.id}>
                <td style={{ fontWeight: 500 }}>{doc.name}</td>
                <td>{doc.date}</td>
                <td>
                  <StatusBadge status={doc.status} />
                </td>
                <td>
                  <div className="actions">
                    {doc.needSign && (
                      <button className="btn btn-primary btn-sm" type="button">
                        Подписать
                      </button>
                    )}
                    <button className="link" type="button">
                      PDF
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 16 }}>
        <Link to="/requests" className="btn btn-secondary">
          Назад к заявкам
        </Link>
      </div>
    </>
  )
}
