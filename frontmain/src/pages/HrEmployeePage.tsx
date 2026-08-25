import { type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { employees } from '../data/mock'

export function HrEmployeePage() {
  const { id } = useParams()
  const emp = employees.find((e) => String(e.id) === id) ?? employees[0]

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    alert('Изменения сохранены (демо без backend)')
  }

  return (
    <>
      <Link to="/hr" className="back-link">
        ← Назад к панели HR
      </Link>

      <div className="page-header">
        <div>
          <h1 className="page-title" style={{ fontSize: 22 }}>
            Карточка сотрудника
          </h1>
          <p className="muted" style={{ margin: '6px 0 0' }}>
            {emp.name} · id {emp.id}
          </p>
        </div>
        <p className="muted" style={{ color: 'var(--primary)', fontWeight: 500 }}>
          HR редактирует: должность, отдел, руководитель
        </p>
      </div>

      <form className="card" onSubmit={onSubmit}>
        <div className="grid-2">
          <div className="field">
            <label>ФИО · только просмотр</label>
            <input defaultValue={emp.name} disabled />
          </div>
          <div className="field">
            <label>Отдел · можно менять</label>
            <input defaultValue={emp.dept} />
          </div>
          <div className="field">
            <label>Email · только просмотр</label>
            <input defaultValue={emp.email} disabled />
          </div>
          <div className="field">
            <label>Должность · можно менять</label>
            <input defaultValue={emp.position} />
          </div>
          <div className="field">
            <label>Телефон · только просмотр</label>
            <input defaultValue={emp.phone} disabled />
          </div>
          <div className="field">
            <label>Руководитель · можно менять</label>
            <input defaultValue={emp.manager} />
          </div>
          <div className="field">
            <label>Дата рождения · только просмотр</label>
            <input defaultValue={emp.birthDate} disabled />
          </div>
          <div className="field">
            <label>Дата поступления · только просмотр</label>
            <input defaultValue={emp.hireDate} disabled />
          </div>
        </div>

        <div className="actions" style={{ marginBottom: 16 }}>
          <button className="btn btn-secondary" type="button">
            Показать ПДн (паспорт, ИНН, СНИЛС)
          </button>
          <span className="muted">Запрос пишется в лог (демо)</span>
        </div>

        <div className="actions">
          <button className="btn btn-primary" type="submit">
            Сохранить изменения
          </button>
          <Link to="/hr" className="btn btn-secondary">
            Отмена
          </Link>
        </div>
      </form>

      <div className="card" style={{ marginTop: 16 }}>
        <h3 className="section-title">При отклонении заявки — комментарий</h3>
        <div className="field" style={{ marginBottom: 0 }}>
          <textarea
            rows={3}
            defaultValue="Недостаточно дней отпуска / пересечение с утверждённым графиком"
            style={{ width: '100%', border: '1px solid var(--border)', borderRadius: 8, padding: 12 }}
          />
        </div>
      </div>
    </>
  )
}
