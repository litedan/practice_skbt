import { useEffect, useState } from 'react'
import { usersApi } from '../api/endpoints'
import { StatusBadge } from '../components/StatusBadge'
import { useAuth } from '../auth/AuthContext'
import { errorMessage } from '../lib/format'
import { hasPermission } from '../lib/permissions'
import type { UserPrivateData } from '../types/api'

type PersonalDocKind = 'passport' | 'snils' | 'military' | 'bank'

type PersonalDoc = {
  kind: PersonalDocKind
  title: string
  subtitle: string
  previewLabel: string
  filled: boolean
  valuePreview: string
}

function buildDocs(data: UserPrivateData | null): PersonalDoc[] {
  const bankParts = [
    data?.account_number,
    data?.bik,
    data?.bank_receiver,
    data?.correspondent_account,
    data?.kpp,
  ].filter(Boolean)

  return [
    {
      kind: 'passport',
      title: 'Паспорт',
      subtitle: 'Удостоверение личности',
      previewLabel: 'Паспорт РФ',
      filled: Boolean(data?.passport?.trim()),
      valuePreview: data?.passport?.trim() || 'Данные не заполнены',
    },
    {
      kind: 'snils',
      title: 'СНИЛС',
      subtitle: 'Страховое свидетельство',
      previewLabel: 'СНИЛС',
      filled: Boolean(data?.snils?.trim()),
      valuePreview: data?.snils?.trim() || 'Данные не заполнены',
    },
    {
      kind: 'military',
      title: 'Военный билет',
      subtitle: 'Воинский учёт',
      previewLabel: 'Военный билет',
      filled: Boolean(data?.military_id?.trim()),
      valuePreview: data?.military_id?.trim() || 'Данные не заполнены',
    },
    {
      kind: 'bank',
      title: 'Банковские реквизиты',
      subtitle: 'Счёт для выплат',
      previewLabel: 'Реквизиты',
      filled: bankParts.length > 0,
      valuePreview: bankParts.length
        ? [data?.bank_receiver, data?.account_number, data?.bik].filter(Boolean).join(' · ')
        : 'Данные не заполнены',
    },
  ]
}

export function DocumentsPage() {
  const { user } = useAuth()
  const [privateData, setPrivateData] = useState<UserPrivateData | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const canPrivate = hasPermission(user, 'private_data:read_self', 'private_data:read_any')

  useEffect(() => {
    if (!user) return
    let cancelled = false
    async function load() {
      setLoading(true)
      setError('')
      try {
        if (!canPrivate) {
          if (!cancelled) setPrivateData(null)
          return
        }
        const data = await usersApi.getPrivate(user!.id)
        if (!cancelled) setPrivateData(data)
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
  }, [user, canPrivate])

  const docs = buildDocs(privateData)

  return (
    <>
      <h1 className="page-title">Документы</h1>
      <p className="muted" style={{ marginTop: 0 }}>
        Паспорт, СНИЛС, военный билет и банковские реквизиты из профиля.
      </p>

      {error && <p className="form-error">{error}</p>}

      {loading && <p className="empty">Загрузка…</p>}

      {!loading && (
        <div className="personal-docs-grid">
          {docs.map((doc) => (
            <article key={doc.kind} className={`personal-doc-card kind-${doc.kind}`}>
              <div className={`personal-doc-preview kind-${doc.kind}`} aria-hidden>
                <div className="personal-doc-preview-inner">
                  <span className="personal-doc-preview-mark">{doc.previewLabel}</span>
                  <span className="personal-doc-preview-lines">
                    <span />
                    <span />
                    <span />
                  </span>
                </div>
              </div>

              <div className="personal-doc-body">
                <div className="page-header" style={{ marginBottom: 8 }}>
                  <div>
                    <h3 className="section-title" style={{ margin: 0 }}>
                      {doc.title}
                    </h3>
                    <p className="muted" style={{ margin: '4px 0 0' }}>
                      {doc.subtitle}
                    </p>
                  </div>
                  <StatusBadge status={doc.filled ? 'Заполнен' : 'Нет данных'} />
                </div>

                <p className="personal-doc-value">{doc.valuePreview}</p>
              </div>
            </article>
          ))}
        </div>
      )}
    </>
  )
}
