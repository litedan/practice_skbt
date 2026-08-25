import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { currentUser } from '../data/mock'

export function RequestCreatePage() {
  const navigate = useNavigate()
  const [type, setType] = useState<'Отпуск' | 'Больничный'>('Отпуск')

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    navigate('/requests')
  }

  return (
    <>
      <h1 className="page-title">Новая заявка</h1>

      <form className="card" style={{ maxWidth: 640, marginTop: 24 }} onSubmit={onSubmit}>
        <div className="actions" style={{ marginBottom: 16 }}>
          <button
            type="button"
            className={type === 'Отпуск' ? 'btn btn-primary' : 'btn btn-secondary'}
            onClick={() => setType('Отпуск')}
          >
            Отпуск
          </button>
          <button
            type="button"
            className={type === 'Больничный' ? 'btn btn-primary' : 'btn btn-secondary'}
            onClick={() => setType('Больничный')}
          >
            Больничный
          </button>
        </div>

        {type === 'Отпуск' && (
          <p style={{ color: 'var(--primary)', fontSize: 13, marginTop: 0 }}>
            Доступно дней отпуска: {currentUser.vacationDays}
          </p>
        )}

        {type === 'Отпуск' && (
          <div className="field">
            <label>Тип отпуска</label>
            <select defaultValue="Ежегодный оплачиваемый">
              <option>Ежегодный оплачиваемый</option>
              <option>Без сохранения зарплаты</option>
            </select>
          </div>
        )}

        <div className="grid-2">
          <div className="field">
            <label>Дата начала</label>
            <input type="date" defaultValue="2026-03-10" required />
          </div>
          <div className="field">
            <label>Дата окончания</label>
            <input type="date" defaultValue="2026-03-24" required />
          </div>
        </div>

        <div className="field">
          <label>Комментарий</label>
          <input defaultValue="Семейная поездка" />
        </div>

        <div className="actions">
          <Link to="/requests" className="btn btn-secondary">
            Сохранить черновик
          </Link>
          <button className="btn btn-primary" type="submit">
            Отправить
          </button>
        </div>
      </form>
    </>
  )
}
