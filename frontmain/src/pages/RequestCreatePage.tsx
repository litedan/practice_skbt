import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { dictionariesApi, documentsApi, requestsApi } from '../api/endpoints'
import { errorMessage } from '../lib/format'
import type { RequestTypeItem, TemplateItem } from '../types/api'

// Приводит значение <input type="date"> (YYYY-MM-DD) к формату ДД.ММ.ГГГГ,
// который используют шаблоны документов.
function toRuDate(value: string) {
  const [year, month, day] = value.split('-')
  if (!year || !month || !day) return value
  return `${day}.${month}.${year}`
}

export function RequestCreatePage() {
  const navigate = useNavigate()
  const [types, setTypes] = useState<RequestTypeItem[]>([])
  const [typeId, setTypeId] = useState<number | ''>('')
  const [comment, setComment] = useState('')
  const [file, setFile] = useState<File | null>(null)

  const [templates, setTemplates] = useState<TemplateItem[]>([])
  const [templateCode, setTemplateCode] = useState('')
  const [templateFields, setTemplateFields] = useState<Record<string, string>>({})

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

    dictionariesApi
      .templates()
      .then((items) => setTemplates(items))
      .catch((err) => setError(errorMessage(err)))
  }, [])

  const selectedType = types.find((item) => item.id === typeId)
  const isApplication = selectedType?.name === 'Заявление'
  const selectedTemplate = templates.find((t) => t.code === templateCode) ?? null

  function onTypeChange(id: number) {
    setTypeId(id)
    setTemplateCode('')
    setTemplateFields({})
  }

  function onTemplateChange(code: string) {
    setTemplateCode(code)
    setTemplateFields({})
  }

  function onFieldChange(key: string, value: string) {
    setTemplateFields((prev) => ({ ...prev, [key]: value }))
  }

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

      if (selectedTemplate) {
        const context: Record<string, string> = {}
        for (const field of selectedTemplate.fields) {
          const raw = templateFields[field.key]?.trim() ?? ''
          context[field.key] = field.type === 'date' && raw ? toRuDate(raw) : raw
        }
        await documentsApi.generateDocument(created.id, {
          template_code: selectedTemplate.code,
          context,
        })
      }

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
        <div className="field">
          <label>Тип заявки</label>
          <select value={typeId} onChange={(e) => onTypeChange(Number(e.target.value))} required>
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

        {isApplication && (
          <div className="field">
            <label>Шаблон документа (необязательно)</label>
            <select value={templateCode} onChange={(e) => onTemplateChange(e.target.value)}>
              <option value="">Без шаблона</option>
              {templates.map((tpl) => (
                <option key={tpl.code} value={tpl.code}>
                  {tpl.name}
                </option>
              ))}
            </select>
            <span className="muted">
              Документ будет автоматически сформирован по выбранному шаблону и прикреплён к заявке.
            </span>
          </div>
        )}

        {isApplication && selectedTemplate && selectedTemplate.fields.length > 0 && (
          <div className="card" style={{ background: 'var(--surface-muted, #f7f7f9)', marginBottom: 16 }}>
            <p className="muted" style={{ marginTop: 0 }}>
              Заполните данные для документа «{selectedTemplate.name}». Остальные данные (ФИО, должность,
              организация, дата) подставятся автоматически.
            </p>
            {selectedTemplate.fields.map((field) => (
              <div className="field" key={field.key}>
                <label>{field.label}</label>
                <input
                  type={field.type === 'number' ? 'number' : field.type === 'date' ? 'date' : 'text'}
                  value={templateFields[field.key] ?? ''}
                  onChange={(e) => onFieldChange(field.key, e.target.value)}
                  required={field.required}
                />
              </div>
            ))}
          </div>
        )}

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
