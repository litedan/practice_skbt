import { REQUEST_STATUS, type DictionaryItem, type RequestRead, type Role } from '../types/api'

export type RequestAction = {
  label: string
  statusName: string
  kind: 'primary' | 'secondary' | 'danger'
}

export function statusIdByName(statuses: DictionaryItem[], name: string) {
  return statuses.find((item) => item.name === name)?.id
}

export function actionsForRequest(request: RequestRead, role: Role): RequestAction[] {
  const status = request.status.name

  if (role === 'hr') {
    if (status === REQUEST_STATUS.CREATED) {
      return [
        { label: 'Взять на проверку', statusName: REQUEST_STATUS.IN_REVIEW, kind: 'primary' },
        { label: 'Отклонить', statusName: REQUEST_STATUS.REJECTED, kind: 'danger' },
      ]
    }
    if (status === REQUEST_STATUS.IN_REVIEW) {
      return [
        { label: 'На согласование', statusName: REQUEST_STATUS.IN_APPROVAL, kind: 'primary' },
        { label: 'Вернуть', statusName: REQUEST_STATUS.CREATED, kind: 'secondary' },
        { label: 'Отклонить', statusName: REQUEST_STATUS.REJECTED, kind: 'danger' },
      ]
    }
    if (status === REQUEST_STATUS.APPROVED) {
      return [{ label: 'Закрыть', statusName: REQUEST_STATUS.CLOSED, kind: 'primary' }]
    }
    if (status === REQUEST_STATUS.REJECTED) {
      return [{ label: 'Вернуть в работу', statusName: REQUEST_STATUS.CREATED, kind: 'secondary' }]
    }
  }

  if (role === 'manager' && status === REQUEST_STATUS.IN_APPROVAL) {
    return [
      { label: 'Одобрить', statusName: REQUEST_STATUS.APPROVED, kind: 'primary' },
      { label: 'Отклонить', statusName: REQUEST_STATUS.REJECTED, kind: 'danger' },
    ]
  }

  return []
}
