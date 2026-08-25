import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { dictionariesApi, requestsApi } from '../api/endpoints'
import { errorMessage } from '../lib/format'
import type { RequestTypeItem } from '../types/api'

export function RequestCreatePage() {
  const navigate = useNavigate()
  const [types, setTypes] = useState<RequestTypeItem[]>([])
  const [typeId, setTypeId] = useState<number | ''>('')
  const [comment, setComment] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)

  useEffect(() => {
    dictionariesApi
      .requestTypes()
      .then((items) => {
        setTypes(items)
        if (items[0]) setTypeId(items[0].id)
      })
      .catch((err) => setError(errorMessage(err)))
  }, [])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (typeId === '') return
    setError('')
    setPending(true)
    try {
      const created = await requestsApi.create({
        request_type_id: typeId,
        comment: comment.trim() || undefined,
      })
      if (file) await requestsApi.upload(created.id, file)
      navigate(`/requests/${created.id}`)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPending(false)
    }
  }

  return (
    <>
      <h1 className="page-title">Новая заявка</h1>

      <form className="card" style={{ maxWidth: 640, marginTop: 24 }} onSubmit={(e) => void onSubmit(e)}>
        <p className="muted" style={{ marginTop: 0 }}>
          Бэкенд принимает тип заявки и комментарий. Период отпуска и черновик в API пока не предусмотрены.
        </p>

        <div className="field">
          <label>Тип заявки</label>
          <select value={typeId} onChange={(e) => setTypeId(Number(e.target.value))} required>
            {types.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label>Комментарий</label>
          <textarea rows={4} value={comment} onChange={(e) => setComment(e.target.value)} />
        </div>

        <div className="field">
          <label>Файл (необязательно)</label>
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          <span className="muted">pdf, jpg, png, doc, docx · до 10 МБ</span>
        </div>

        {error && <p className="form-error">{error}</p>}

        <div className="actions">
          <Link to="/requests" className="btn btn-secondary">
            Отмена
          </Link>
          <button className="btn btn-primary" type="submit" disabled={pending || typeId === ''}>
            {pending ? 'Отправка…' : 'Отправить'}
          </button>
        </div>
      </form>
    </>
  )
}
