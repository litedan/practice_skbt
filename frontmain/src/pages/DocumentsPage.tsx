import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { requestsApi } from '../api/endpoints'
import { errorMessage } from '../lib/format'
import type { DocumentFile, RequestRead } from '../types/api'

async function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

type Row = DocumentFile & { requestType: string }

export function DocumentsPage() {
  const [rows, setRows] = useState<Row[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const list: RequestRead[] = await requestsApi.list()
        const details = await Promise.all(list.map((item) => requestsApi.get(item.id)))
        if (cancelled) return
        setRows(
          details.flatMap((req) =>
            req.document_files.map((file) => ({ ...file, requestType: req.request_type.name })),
          ),
        )
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
  }, [])

  return (
    <>
      <h1 className="page-title">Вложения</h1>
      <p className="muted">
        Отдельного каталога документов в API нет. Здесь файлы, прикреплённые к заявкам.
      </p>

      {error && <p className="form-error">{error}</p>}

      <div className="card">
        {loading && <p className="empty">Загрузка…</p>}
        {!loading && rows.length === 0 && <p className="empty">Вложений нет</p>}
        {!loading && rows.length > 0 && (
          <table className="table">
            <thead>
              <tr>
                <th>Файл</th>
                <th>Заявка</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={`${row.request_id}-${row.id}`}>
                  <td style={{ fontWeight: 500 }}>{row.name}</td>
                  <td>
                    <Link to={`/requests/${row.request_id}`} style={{ color: 'var(--primary)' }}>
                      {row.requestType} #{row.request_id}
                    </Link>
                  </td>
                  <td>
                    <button
                      className="link"
                      type="button"
                      onClick={() => {
                        void requestsApi.download(row.request_id, row.id).then((blob) => saveBlob(blob, row.name))
                      }}
                    >
                      Скачать
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  )
}
