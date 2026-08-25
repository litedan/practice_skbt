import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { errorMessage } from '../lib/format'

export function LoginPage() {
  const { login, isAuth, ready } = useAuth()
  const navigate = useNavigate()
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState('employee@kedo.local')
  const [password, setPassword] = useState('Password123!')
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)

  if (ready && isAuth) return <Navigate to="/" replace />

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setPending(true)
    try {
      await login(email, password)
      navigate('/')
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={(e) => void onSubmit(e)}>
        <h1>Практика</h1>
        <p className="subtitle">Личный кабинет сотрудника</p>

        <div className="field">
          <label>Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>

        <div className="field">
          <label>Пароль</label>
          <div className="password-wrap">
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
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
                  <path d="M3 3l18 18" stroke="#9CA3AF" strokeWidth="1.5" strokeLinecap="round" />
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
                  <circle cx="12" cy="12" r="3" stroke="#9CA3AF" strokeWidth="1.5" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {error && <p className="form-error">{error}</p>}

        <button className="btn btn-primary" style={{ width: '100%' }} type="submit" disabled={pending}>
          {pending ? 'Вход…' : 'Войти'}
        </button>

        <p className="muted" style={{ marginTop: 16, fontSize: 12 }}>
          employee@kedo.local · manager@kedo.local · hr@kedo.local · admin@kedo.local
          <br />
          пароль Password123!
        </p>
      </form>
    </div>
  )
}
