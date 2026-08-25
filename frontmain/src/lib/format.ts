export function formatDate(value: string | null | undefined) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString('ru-RU')
}

export function formatDateTime(value: string | null | undefined) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' })
}

export function firstName(fullName: string) {
  return fullName.split(' ')[1] || fullName.split(' ')[0] || fullName
}

export function roleLabel(role: string) {
  const map: Record<string, string> = {
    employee: 'Сотрудник',
    hr: 'HR',
    manager: 'Руководитель',
    admin: 'Администратор',
  }
  return map[role] ?? role
}

export function errorMessage(err: unknown) {
  if (err instanceof Error) return err.message
  return 'Неизвестная ошибка'
}
