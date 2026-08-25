export type Role = 'employee' | 'hr' | 'manager' | 'admin'

export type DictionaryItem = {
  id: number
  name: string
}

export type RequestTypeItem = DictionaryItem & {
  file_path: string | null
}

export type UserRead = {
  id: number
  email: string | null
  full_name: string
  phone: string | null
  birth_date: string | null
  city: string | null
  hire_date: string | null
  department_id: number | null
  position_id: number | null
  role: Role
  is_blocked: boolean
  blocked_at: string | null
  block_reason: string | null
  department: DictionaryItem | null
  position: DictionaryItem | null
}

export type UserMe = UserRead & {
  permissions: string[]
}

export type UserPrivateData = {
  id: number
  user_id: number
  passport: string | null
  inn: string | null
  snils: string | null
  bank_account: string | null
  military_id: string | null
  account_number: string | null
  bik: string | null
  bank_receiver: string | null
  correspondent_account: string | null
  kpp: string | null
  contract_number: string | null
  dismissal_date: string | null
  personal_data_deletion_date: string | null
}

export type StatusBrief = {
  id: number
  name: string
}

export type RequestTypeBrief = {
  id: number
  name: string
  file_path: string | null
}

export type UserBrief = {
  id: number
  full_name: string
  email: string | null
}

export type DocumentFile = {
  id: number
  name: string
  request_id: number
}

export type RequestRead = {
  id: number
  comment: string | null
  employee_id: number
  reviewer_id: number | null
  approver_id: number | null
  status_id: number
  request_type_id: number
  created_at: string
  updated_at: string
  status: StatusBrief
  request_type: RequestTypeBrief
  employee: UserBrief | null
  reviewer: UserBrief | null
  approver: UserBrief | null
}

export type RequestDetail = RequestRead & {
  document_files: DocumentFile[]
}

export type RequestStats = {
  total: number
  created: number
  in_review: number
  in_approval: number
  approved: number
  rejected: number
  closed: number
}

export type NotificationItem = {
  id: number
  title: string
  message: string
  is_read: boolean
  created_at: string
  user_id: number
  request_id: number | null
}

export type AuditLog = {
  id: number
  entity_name: string
  entity_id: number
  action: string
  old_data: Record<string, unknown> | null
  new_data: Record<string, unknown> | null
  user_id: number | null
  ip_address: string | null
  user_agent: string | null
  created_at: string
}

export const REQUEST_STATUS = {
  CREATED: 'Создана',
  IN_REVIEW: 'На проверке',
  IN_APPROVAL: 'На согласовании',
  APPROVED: 'Одобрена',
  REJECTED: 'Отклонена',
  CLOSED: 'Закрыта',
} as const
