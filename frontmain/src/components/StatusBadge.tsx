type Props = {
  status: string
}

export function StatusBadge({ status }: Props) {
  let cls = 'badge badge-info'
  const lower = status.toLowerCase()

  if (
    lower.includes('проверк') ||
    lower.includes('соглас') ||
    lower.includes('создан') ||
    lower.includes('подпис') ||
    lower.includes('приказ')
  ) {
    cls = 'badge badge-warn'
  } else if (
    lower.includes('одобр') ||
    lower.includes('закрыт') ||
    lower.includes('готов') ||
    lower.includes('активен') ||
    lower.includes('подписан')
  ) {
    cls = 'badge badge-ok'
  } else if (lower.includes('отклон') || lower.includes('блок')) {
    cls = 'badge badge-bad'
  }

  return <span className={cls}>{status}</span>
}
