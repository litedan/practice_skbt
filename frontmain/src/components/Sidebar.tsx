import { NavLink } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import type { Role } from '../data/mock'

type NavItem = {
  to: string
  label: string
  roles?: Role[]
}

const items: NavItem[] = [
  { to: '/', label: 'Главная' },
  { to: '/requests', label: 'Мои заявки' },
  { to: '/documents', label: 'Документы' },
  { to: '/profile', label: 'Профиль' },
  { to: '/hr', label: 'HR', roles: ['hr', 'admin'] },
  { to: '/admin', label: 'Админ', roles: ['admin'] },
]

export function Sidebar() {
  const { role, logout } = useAuth()

  const visible = items.filter((item) => {
    if (!item.roles) return true
    return item.roles.includes(role)
  })

  return (
    <aside className="sidebar">
      <p className="sidebar-brand">Практика</p>
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
      <button className="nav-link" style={{ marginTop: 'auto', textAlign: 'left' }} onClick={logout}>
        Выйти
      </button>
    </aside>
  )
}
