import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { documentsApi, requestsApi } from '../api/endpoints'
import { StatusBadge } from '../components/StatusBadge'
import { useAuth } from '../auth/AuthContext'
import { errorMessage, formatDate } from '../lib/format'
import { REQUEST_STATUS, type DocumentFile, type RequestDetail } from '../types/api'

type DocFilter = 'all' | 'to_sign' | 'signed'

type FormedDocument = {
  id: number
  title: string
  date: string
  status: 'На подпись' | 'Подписан' | 'Готов'
  requestId: number
  file: DocumentFile | null
}

const SIGNED_KEY = 'kedo_signed_docs'

function loadSignedIds(): Set<number> {
  try {
    const raw = localStorage.getItem(SIGNED_KEY)
    if (!raw) return new Set()
    return new Set(JSON.parse(raw) as number[])
  } catch {
    return new Set()
  }
}

function saveSignedIds(ids: Set<number>) {
  localStorage.setItem(SIGNED_KEY, JSON.stringify([...ids]))
}

function mapDocument(req: RequestDetail, signedIds: Set<number>): FormedDocument | null {
  const statusName = req.status.name
  if (
    statusName !== REQUEST_STATUS.APPROVED &&
    statusName !== REQUEST_STATUS.CLOSED &&
    !signedIds.has(req.id)
  ) {
    return null
  }

  const file = req.document_files[0] ?? null
  let status: FormedDocument['status']
  if (signedIds.has(req.id) || statusName === REQUEST_STATUS.CLOSED) {
    status = file ? 'Готов' : 'Подписан'
  } else {
    status = 'На подпись'
  }

  return {
    id: req.id,
    title: `${req.request_type.name} №${req.id}`,
    date: req.updated_at || req.created_at,
    status,
    requestId: req.id,
    file,
  }
}

async function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export function DocumentsPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [filter, setFilter] = useState<DocFilter>('all')
  const [docs, setDocs] = useState<FormedDocument[]>([])
  const [signedIds, setSignedIds] = useState<Set<number>>(() => loadSignedIds())
  const [error, setError] = useState('')
  const [info, setInfo] = useState('')
  const [loading, setLoading] = useState(true)
  const [pendingId, setPendingId] = useState<number | null>(null)

  useEffect(() => {
    if (!user) return
    let cancelled = false
    async function load() {
      setLoading(true)
      setError('')
      try {
        const list = await requestsApi.list()
        const mine = list.filter((item) => item.employee_id === user!.id)
        const details = await Promise.all(mine.map((item) => requestsApi.get(item.id)))
        if (cancelled) return
        const formed = details
          .map((req) => mapDocument(req, signedIds))
          .filter((item): item is FormedDocument => item != null)
          .sort((a, b) => b.date.localeCompare(a.date))
        setDocs(formed)
      } catch (err) {
        if (!cancelled) setError(errorMessage(err))
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [user, signedIds])

  const visible = useMemo(() => {
    if (filter === 'to_sign') return docs.filter((d) => d.status === 'На подпись')
    if (filter === 'signed') return docs.filter((d) => d.status === 'Подписан' || d.status === 'Готов')
    return docs
  }, [docs, filter])

  async function onSign(doc: FormedDocument) {
    setPendingId(doc.id)
    setError('')
    setInfo('')
    try {
      const res = await documentsApi.sign(doc.id)
      const next = new Set(signedIds)
      next.add(doc.id)
      setSignedIds(next)
      saveSignedIds(next)
      setInfo(res.message || 'Документ отмечен как подписанный')
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPendingId(null)
    }
  }

  async function onPdf(doc: FormedDocument) {
    if (!doc.file) {
      setInfo('PDF ещё не сформирован — файл появится позже')
      setError('')
      return
    }
    setError('')
    setInfo('')
    const blob = await requestsApi.download(doc.requestId, doc.file.id)
    await saveBlob(blob, doc.file.name)
  }

  return (
    <>
      <h1 className="page-title">Документы</h1>

      <div className="tabs">
        {(
          [
            ['all', 'Все'],
            ['to_sign', 'На подпись'],
            ['signed', 'Подписанные'],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={filter === id ? 'tab active' : 'tab'}
            onClick={() => setFilter(id)}
          >
            {label}
          </button>
        ))}
      </div>

      {error && <p className="form-error">{error}</p>}
      {info && <p className="form-ok">{info}</p>}

      <div className="card">
        {loading && <p className="empty">Загрузка…</p>}
        {!loading && visible.length === 0 && <p className="empty">Документов нет</p>}
        {!loading &&
          visible.map((doc) => (
            <div key={doc.id} className="doc-row">
              <div>
                <div style={{ fontWeight: 600 }}>{doc.title}</div>
                <div className="muted" style={{ marginTop: 4 }}>
                  {formatDate(doc.date)}
                </div>
              </div>
              <StatusBadge status={doc.status} />
              <div className="actions">
                {doc.status === 'На подпись' && (
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    disabled={pendingId === doc.id}
                    onClick={() => void onSign(doc)}
                  >
                    Подписать
                  </button>
                )}
                {doc.status === 'На подпись' && (
                  <button
                    type="button"
                    className="link"
                    onClick={() => navigate(`/requests/${doc.requestId}`)}
                  >
                    Редактировать
                  </button>
                )}
                <button type="button" className="badge badge-pdf" onClick={() => void onPdf(doc)}>
                  PDF
                </button>
              </div>
            </div>
          ))}
      </div>
    </>
  )
}
