type Props = {
  status: string
}

export function StatusBadge({ status }: Props) {
  let cls = 'badge badge-info'

  if (status.includes('рассмотр') || status.includes('подпис') || status.includes('приказ')) {
    cls = 'badge badge-warn'
  } else if (status.includes('Одобр') || status.includes('Готов') || status.includes('Подписан')) {
    cls = 'badge badge-ok'
  } else if (status.includes('Отклон') || status.includes('Блок')) {
    cls = 'badge badge-bad'
  }

  return <span className={cls}>{status}</span>
}
