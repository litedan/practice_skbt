import { api, apiDownload, setTokens, clearTokens, getRefreshToken } from './client'
import type {
  AuditLog,
  DictionaryItem,
  DocumentFile,
  NotificationItem,
  RequestDetail,
  RequestRead,
  RequestStats,
  RequestTypeItem,
  TemplateItem,
  UserMe,
  UserPrivateData,
  UserRead,
} from '../types/api'

export type GenerateRequestDocumentPayload = {
  template_code: string
  context: Record<string, unknown>
}

export type GeneratedRequestDocument = {
  id: number
  name: string
  request_id: number
  file_path: string
}

export async function login(email: string, password: string) {
  const tokens = await api.post<{ access_token: string; refresh_token: string }>(
    '/auth/login',
    { email, password },
    { auth: false, skipRefresh: true },
  )
  setTokens(tokens.access_token, tokens.refresh_token)
  return tokens
}

export async function logout() {
  try {
    await api.post('/auth/logout', { refresh_token: getRefreshToken() })
  } finally {
    clearTokens()
  }
}

export const usersApi = {
  me: () => api.get<UserMe>('/users/me'),
  updateMe: (body: { phone?: string | null; city?: string | null }) =>
    api.patch<UserMe>('/users/me', body),
  changePassword: (body: { current_password: string; new_password: string }) =>
    api.post<{ detail: string }>('/users/me/change-password', body),
  get: (id: number) => api.get<UserRead>(`/users/${id}`),
  getPrivate: (id: number) => api.get<UserPrivateData>(`/users/${id}/private-data`),
  updatePrivate: (id: number, body: Partial<UserPrivateData>) =>
    api.put<UserPrivateData>(`/users/${id}/private-data`, body),
}

export const dictionariesApi = {
  departments: () => api.get<DictionaryItem[]>('/dictionaries/departments'),
  positions: () => api.get<DictionaryItem[]>('/dictionaries/positions'),
  requestTypes: () => api.get<RequestTypeItem[]>('/dictionaries/request-types'),
  statuses: () => api.get<DictionaryItem[]>('/dictionaries/statuses'),
  templates: () => api.get<TemplateItem[]>('/dictionaries/templates'),
}

export const requestsApi = {
  list: (params?: { status_id?: number; request_type_id?: number; employee_id?: number }) => {
    const query = new URLSearchParams()
    if (params?.status_id != null) query.set('status_id', String(params.status_id))
    if (params?.request_type_id != null) query.set('request_type_id', String(params.request_type_id))
    if (params?.employee_id != null) query.set('employee_id', String(params.employee_id))
    const suffix = query.toString() ? `?${query}` : ''
    return api.get<RequestRead[]>(`/requests${suffix}`)
  },
  get: (id: number) => api.get<RequestDetail>(`/requests/${id}`),
  create: (body: { request_type_id: number; comment?: string }) =>
    api.post<RequestRead>('/requests', body),
  update: (id: number, body: { status_id?: number; comment?: string | null }) =>
    api.patch<RequestRead>(`/requests/${id}`, body),
  stats: () => api.get<RequestStats>('/requests/stats'),
  files: (id: number) => api.get<DocumentFile[]>(`/requests/${id}/files`),
  upload: (id: number, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.postForm<DocumentFile>(`/requests/${id}/files`, form)
  },
  download: (requestId: number, fileId: number) => apiDownload(`/requests/${requestId}/files/${fileId}`),
}

export const documentsApi = {
  sign: (documentId: number) =>
    api.post<{ document_id: number; status: string; message: string; signed_at: string | null }>(
      `/documents/${documentId}/sign`,
    ),
        generateDocument: (
    id: number,
    body: GenerateRequestDocumentPayload,
  ) =>
    api.post<GeneratedRequestDocument>(
      `/requests/${id}/generate-document`,
      body,
    ),

}

export const notificationsApi = {
  list: () => api.get<NotificationItem[]>('/notifications'),
  markRead: (id: number) => api.patch<{ detail: string }>(`/notifications/${id}/read`),
}

export const adminApi = {
  users: (search?: string) => {
    const q = search ? `?search=${encodeURIComponent(search)}` : ''
    return api.get<UserRead[]>(`/admin/users${q}`)
  },
  updateUser: (
    id: number,
    body: { department_id?: number | null; position_id?: number | null; is_blocked?: boolean; block_reason?: string },
  ) => api.patch<UserRead>(`/admin/users/${id}`, body),
  audit: () => api.get<AuditLog[]>('/admin/audit?limit=50'),
}
