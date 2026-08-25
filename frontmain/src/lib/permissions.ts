import type { UserMe } from '../types/api'

export function hasPermission(user: UserMe | null, ...permissions: string[]) {
  if (!user) return false
  return permissions.some((item) => user.permissions.includes(item))
}
