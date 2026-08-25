import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './AuthContext'
import type { Role } from '../types/api'

export function ProtectedRoute({ roles }: { roles?: Role[] }) {
  const { isAuth, ready, role } = useAuth()

  if (!ready) return <p className="muted">Загрузка…</p>
  if (!isAuth) return <Navigate to="/login" replace />
  if (roles && !roles.includes(role)) return <Navigate to="/" replace />

  return <Outlet />
}
