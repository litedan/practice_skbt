import { Link } from 'react-router-dom'
import { employees, hrRequests } from '../data/mock'
import { StatusBadge } from '../components/StatusBadge'

export function HrPanelPage() {
  return (
    <>
      <div className="page-header">
        <h1 className="page-title">HR — Панель</h1>
        <div className="muted">Петрова А.С. · HR</div>
      </div>

      <div className="grid-4">
        {[
          ['5', 'Новые заявки'],
          ['3', 'На согласовании'],
          ['2', 'Ожидают подписи'],
          ['4', 'Оформлено сегодня'],
        ].map(([value, label]) => (
          <div className="card" key={label}>
            <p className="stat-value">{value}</p>
            <p className="stat-label">{label}</p>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h3 className="section-title">Очередь заявок</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Сотрудник</th>
              <th>Тип</th>
              <th>Период</th>
              <th>Согласующий</th>
              <th>Статус</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {hrRequests.map((row) => (
              <tr key={row.employee + row.type}>
                <td style={{ fontWeight: 500 }}>{row.employee}</td>
                <td>{row.type}</td>
                <td>{row.period}</td>
                <td>{row.manager}</td>
                <td>
                  <StatusBadge status={row.status} />
                </td>
                <td>
                  <div className="actions">
                    {row.canAct ? (
                      <>
                        <button className="btn btn-primary btn-sm" type="button">
                          Одобрить
                        </button>
                        <button className="btn btn-secondary btn-sm" type="button">
                          Отклонить
                        </button>
                      </>
                    ) : (
                      <button className="btn btn-primary btn-sm" type="button">
                        Сформировать приказ
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <div className="page-header" style={{ marginBottom: 8 }}>
          <h3 className="section-title" style={{ margin: 0 }}>
            Сотрудники
          </h3>
          <span className="muted">Нажмите «Открыть» → карточка сотрудника</span>
        </div>
        <table className="table">
          <thead>
            <tr>
              <th>ФИО</th>
              <th>Отдел</th>
              <th>Должность</th>
              <th>Руководитель</th>
              <th>Email</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {employees.map((emp) => (
              <tr key={emp.id}>
                <td style={{ fontWeight: 500 }}>{emp.name}</td>
                <td>{emp.dept}</td>
                <td>{emp.position}</td>
                <td>{emp.manager}</td>
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
    </>
  )
}
