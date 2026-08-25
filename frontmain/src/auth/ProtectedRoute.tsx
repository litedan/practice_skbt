import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import type { Role } from '../data/mock'

export function ProtectedRoute({ roles }: { roles?: Role[] }) {
  const { isAuth, role } = useAuth()

  if (!isAuth) return <Navigate to="/login" replace />
  if (roles && !roles.includes(role)) return <Navigate to="/" replace />

  return <Outlet />
}
