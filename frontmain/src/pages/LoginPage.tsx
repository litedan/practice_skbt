import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import type { Role } from '../data/mock'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [showPassword, setShowPassword] = useState(false)
  const [role, setRole] = useState<Role>('employee')

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    login(role)
    navigate('/')
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={onSubmit}>
        <h1>Практика</h1>
        <p className="subtitle">Личный кабинет сотрудника</p>

        <div className="field">
          <label>Email</label>
          <input type="email" defaultValue="example@mail.ru" required />
        </div>

        <div className="field">
          <label>Пароль</label>
          <div className="password-wrap">
            <input
              type={showPassword ? 'text' : 'password'}
              defaultValue="password"
              required
            />
            <button
              type="button"
              className="eye-btn"
              onClick={() => setShowPassword((v) => !v)}
              aria-label={showPassword ? 'Скрыть пароль' : 'Показать пароль'}
            >
              {showPassword ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M3 3l18 18"
                    stroke="#9CA3AF"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                  />
                  <path
                    d="M10.6 10.7a2 2 0 0 0 2.8 2.8"
                    stroke="#9CA3AF"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                  />
                  <path
                    d="M9.9 5.2A10.4 10.4 0 0 1 12 5c7 0 10 7 10 7a18.3 18.3 0 0 1-3.2 4.1M6.1 6.1A18 18 0 0 0 2 12s3 7 10 7a9.7 9.7 0 0 0 4.3-1"
                    stroke="#9CA3AF"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"
                    stroke="#9CA3AF"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <circle
                    cx="12"
                    cy="12"
                    r="3"
                    stroke="#9CA3AF"
                    strokeWidth="1.5"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>

        <div className="field">
          <label>Войти как (для демо)</label>
          <select value={role} onChange={(e) => setRole(e.target.value as Role)}>
            <option value="employee">Сотрудник</option>
            <option value="hr">HR</option>
            <option value="admin">Администратор</option>
          </select>
        </div>

        <button className="btn btn-primary" style={{ width: '100%' }} type="submit">
          Войти
        </button>
      </form>
    </div>
  )
}
