import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { login as loginRequest, logout as logoutRequest, usersApi } from '../api/endpoints'
import { clearTokens, getAccessToken } from '../api/client'
import type { Role, UserMe } from '../types/api'

type AuthContextValue = {
  isAuth: boolean
  ready: boolean
  user: UserMe | null
  role: Role
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserMe | null>(null)
  const [ready, setReady] = useState(false)

  const loadUser = useCallback(async () => {
    if (!getAccessToken()) {
      setUser(null)
      return
    }
    const me = await usersApi.me()
    setUser(me)
  }, [])

  useEffect(() => {
    loadUser()
      .catch(() => {
        clearTokens()
        setUser(null)
      })
      .finally(() => setReady(true))
  }, [loadUser])

  const value = useMemo<AuthContextValue>(
    () => ({
      isAuth: Boolean(user),
      ready,
      user,
      role: user?.role ?? 'employee',
      login: async (email, password) => {
        await loginRequest(email, password)
        await loadUser()
      },
      logout: async () => {
        await logoutRequest()
        setUser(null)
      },
      refreshUser: loadUser,
    }),
    [loadUser, ready, user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
