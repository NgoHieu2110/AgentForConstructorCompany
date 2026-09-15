export function formatVnd(value) {
  if (value == null || Number.isNaN(Number(value))) return '—'
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(Number(value))
}

export function formatDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return String(value)
  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(d)
}

export function criterionOf(row, name) {
  return row?.criterion_breakdown?.find((c) => c.criterion === name)
}

export function riskScore(row) {
  const item = criterionOf(row, 'Rủi ro chậm/lỗi')
  if (!item) return null
  return 1 - item.normalized_score
}

export function sourceLabel(computedBy) {
  if (computedBy === 'rule_based') return 'Rule-based'
  if (computedBy === 'ml_model') return 'ML model'
  if (computedBy === 'llm') return 'LLM'
  return computedBy || '—'
}
