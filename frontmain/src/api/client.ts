const API_BASE = import.meta.env.VITE_API_BASE ?? '/api/v1'

const ACCESS_KEY = 'kedo_access_token'
const REFRESH_KEY = 'kedo_refresh_token'

export class ApiError extends Error {
  status: number
  code?: string

  constructor(message: string, status: number, code?: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY)
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY)
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem(ACCESS_KEY, access)
  localStorage.setItem(REFRESH_KEY, refresh)
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

function parseDetail(data: unknown): { message: string; code?: string } {
  if (!data || typeof data !== 'object') return { message: 'Ошибка запроса' }
  const body = data as { detail?: unknown; code?: string }
  if (typeof body.detail === 'string') return { message: body.detail, code: body.code }
  if (Array.isArray(body.detail)) {
    const parts = body.detail.map((item) => {
      if (item && typeof item === 'object' && 'msg' in item) return String((item as { msg: string }).msg)
      return String(item)
    })
    return { message: parts.join('. ') || 'Ошибка валидации', code: body.code }
  }
  return { message: 'Ошибка запроса', code: body.code }
}

type RequestOptions = {
  method?: string
  body?: unknown
  formData?: FormData
  auth?: boolean
  skipRefresh?: boolean
}

let refreshPromise: Promise<boolean> | null = null

async function tryRefresh(): Promise<boolean> {
  const refresh = getRefreshToken()
  if (!refresh) return false
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh }),
  })
  if (!res.ok) {
    clearTokens()
    return false
  }
  const data = (await res.json()) as { access_token: string; refresh_token: string }
  setTokens(data.access_token, data.refresh_token)
  return true
}

async function rawRequest(path: string, options: RequestOptions = {}): Promise<Response> {
  const headers = new Headers()
  if (!options.formData) headers.set('Content-Type', 'application/json')
  if (options.auth !== false) {
    const token = getAccessToken()
    if (token) headers.set('Authorization', `Bearer ${token}`)
  }

  return fetch(`${API_BASE}${path}`, {
    method: options.method ?? 'GET',
    headers,
    body: options.formData ?? (options.body !== undefined ? JSON.stringify(options.body) : undefined),
  })
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  let res = await rawRequest(path, options)

  if (res.status === 401 && options.auth !== false && !options.skipRefresh) {
    if (!refreshPromise) {
      refreshPromise = tryRefresh().finally(() => {
        refreshPromise = null
      })
    }
    const ok = await refreshPromise
    if (ok) res = await rawRequest(path, options)
  }

  if (res.status === 204) return undefined as T

  const contentType = res.headers.get('content-type') ?? ''
  const isJson = contentType.includes('application/json')
  const data = isJson ? await res.json() : null

  if (!res.ok) {
    const { message, code } = parseDetail(data)
    throw new ApiError(message, res.status, code)
  }

  return data as T
}

export async function apiDownload(path: string): Promise<Blob> {
  let res = await rawRequest(path)

  if (res.status === 401) {
    if (!refreshPromise) {
      refreshPromise = tryRefresh().finally(() => {
        refreshPromise = null
      })
    }
    const ok = await refreshPromise
    if (ok) res = await rawRequest(path)
  }

  if (!res.ok) {
    const data = (res.headers.get('content-type') ?? '').includes('application/json')
      ? await res.json()
      : null
    const { message, code } = parseDetail(data)
    throw new ApiError(message, res.status, code)
  }

  return res.blob()
}

export const api = {
  get: <T>(path: string) => apiRequest<T>(path),
  post: <T>(path: string, body?: unknown, opts?: { auth?: boolean; skipRefresh?: boolean }) =>
    apiRequest<T>(path, { method: 'POST', body, ...opts }),
  patch: <T>(path: string, body?: unknown) => apiRequest<T>(path, { method: 'PATCH', body }),
  put: <T>(path: string, body?: unknown) => apiRequest<T>(path, { method: 'PUT', body }),
  postForm: <T>(path: string, formData: FormData) =>
    apiRequest<T>(path, { method: 'POST', formData }),
}
