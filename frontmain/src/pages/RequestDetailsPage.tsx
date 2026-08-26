import { useEffect, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { requestsApi } from '../api/endpoints'
import { StatusBadge } from '../components/StatusBadge'
import { useAuth } from '../auth/AuthContext'
import { errorMessage, formatDate, formatDateTime } from '../lib/format'
import { REQUEST_STATUS, type RequestDetail } from '../types/api'

async function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export function RequestDetailsPage() {
  const { id } = useParams()
  const { user, role } = useAuth()
  const requestId = Number(id)
  const [item, setItem] = useState<RequestDetail | null>(null)
  const [comment, setComment] = useState('')
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)

  async function load() {
    const detail = await requestsApi.get(requestId)
    setItem(detail)
    setComment(detail.comment ?? '')
  }

  useEffect(() => {
    if (!Number.isFinite(requestId)) return
    load().catch((err) => setError(errorMessage(err)))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [requestId])

  if (!Number.isFinite(requestId)) return <p className="form-error">Некорректный номер заявки</p>
  if (error && !item) return <p className="form-error">{error}</p>
  if (!item) return <p className="empty">Загрузка…</p>

  const isOwner = user?.id === item.employee_id
  const workArea = role === 'hr' || role === 'manager'
  const backTo = workArea && !isOwner ? '/hr' : '/requests'
  const backLabel = backTo === '/hr' ? '← Назад к очереди' : '← Назад к заявкам'
  const canEditComment = isOwner && item.status.name === REQUEST_STATUS.CREATED
  const canUpload =
    isOwner &&
    (item.status.name === REQUEST_STATUS.CREATED || item.status.name === REQUEST_STATUS.IN_REVIEW)

  async function saveComment(e: FormEvent) {
    e.preventDefault()
    setPending(true)
    setError('')
    try {
      await requestsApi.update(item!.id, { comment })
      await load()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPending(false)
    }
  }

  async function onUpload(file: File) {
    setPending(true)
    setError('')
    try {
      await requestsApi.upload(item!.id, file)
      await load()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPending(false)
    }
  }

  async function onDownload(fileId: number, name: string) {
    const blob = await requestsApi.download(item!.id, fileId)
    await saveBlob(blob, name)
  }

  return (
    <>
      <Link to={backTo} className="back-link">
        {backLabel}
      </Link>

      <div className="page-header">
        <div>
          <h1 className="page-title" style={{ fontSize: 22 }}>
            {item.request_type.name} №{item.id}
          </h1>
          <p className="muted" style={{ margin: '6px 0 0' }}>
            Подана {formatDateTime(item.created_at)}
          </p>
        </div>
        <StatusBadge status={item.status.name} />
      </div>

      {error && <p className="form-error">{error}</p>}

      <div className="grid-2">
        <div className="card">
          <h3 className="section-title">Данные заявки</h3>
          <Row label="Тип" value={item.request_type.name} />
          <Row label="Сотрудник" value={item.employee?.full_name ?? '—'} />
          <Row label="Проверяющий" value={item.reviewer?.full_name ?? '—'} />
          <Row label="Согласующий" value={item.approver?.full_name ?? '—'} />
          <Row label="Обновлена" value={formatDate(item.updated_at)} />

          <form onSubmit={(e) => void saveComment(e)} style={{ marginTop: 16 }}>
            <div className="field">
              <label>Комментарий</label>
              <textarea
                rows={3}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                disabled={!canEditComment}
              />
            </div>
            {canEditComment && (
              <button className="btn btn-secondary" type="submit" disabled={pending}>
                Сохранить комментарий
              </button>
            )}
          </form>
        </div>

        <div className="card">
          <h3 className="section-title">Вложения</h3>
          {item.document_files.length === 0 && <p className="empty">Файлов нет</p>}
          {item.document_files.map((file) => (
            <div key={file.id} className="actions" style={{ marginBottom: 8 }}>
              <span>{file.name}</span>
              <button
                className="link"
                type="button"
                onClick={() => void onDownload(file.id, file.name)}
              >
                Скачать
              </button>
            </div>
          ))}
          {canUpload && (
            <div className="field" style={{ marginTop: 12, marginBottom: 0 }}>
              <label>Загрузить файл</label>
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) void onUpload(file)
                  e.target.value = ''
                }}
              />
            </div>
          )}
        </div>
      </div>
    </>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', gap: 16 }}>
      <span className="muted">{label}</span>
      <span style={{ fontWeight: 500, textAlign: 'right' }}>{value}</span>
    </div>
  )
}
