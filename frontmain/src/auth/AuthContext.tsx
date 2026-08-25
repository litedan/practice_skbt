import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'
import type { Role } from '../data/mock'

type AuthContextValue = {
  isAuth: boolean
  role: Role
  login: (role?: Role) => void
  logout: () => void
  setRole: (role: Role) => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuth, setIsAuth] = useState(false)
  const [role, setRole] = useState<Role>('employee')

  const value = useMemo(
    () => ({
      isAuth,
      role,
      login: (nextRole: Role = 'employee') => {
        setRole(nextRole)
        setIsAuth(true)
      },
      logout: () => setIsAuth(false),
      setRole,
    }),
    [isAuth, role],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
