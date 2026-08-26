import { NavLink } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { roleLabel } from '../lib/format'
import { hasPermission } from '../lib/permissions'
import type { Role } from '../types/api'

type NavItem = {
  to: string
  label: string
  roles?: Role[]
  permissions?: string[]
}

const items: NavItem[] = [
  { to: '/', label: 'Главная' },
  {
    to: '/requests',
    label: 'Мои заявки',
    permissions: ['requests:read_self', 'requests:read_any', 'requests:read_department'],
  },
  {
    to: '/documents',
    label: 'Документы',
    permissions: ['requests:read_self', 'requests:read_any', 'requests:read_department'],
  },
  { to: '/profile', label: 'Профиль' },
  { to: '/hr', label: 'HR / согласование', roles: ['hr', 'manager'] },
  { to: '/admin', label: 'Админ', roles: ['admin'] },
]

export function Sidebar() {
  const { role, user, logout } = useAuth()

  const visible = items.filter((item) => {
    if (item.roles && !item.roles.includes(role)) return false
    if (item.permissions && !hasPermission(user, ...item.permissions)) return false
    return true
  })

  return (
    <aside className="sidebar">
      <p className="sidebar-brand">Практика</p>
      {user && (
        <p className="muted" style={{ margin: '0 0 8px', padding: '0 14px' }}>
          {user.full_name}
          <br />
          {roleLabel(role)}
        </p>
      )}
      {visible.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === '/'}
          className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
        >
          {item.label}
        </NavLink>
      ))}
      <button
        className="nav-link"
        style={{ marginTop: 'auto', textAlign: 'left' }}
        onClick={() => {
          void logout()
        }}
      >
        Выйти
      </button>
    </aside>
  )
}
