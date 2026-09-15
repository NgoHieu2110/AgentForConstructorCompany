const API_BASE = import.meta.env.VITE_API_BASE ?? '/backend'

async function request(path, { method = 'GET', body, timeoutMs = 120000 } = {}) {
  let res
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(timeoutMs),
    })
  } catch (e) {
    if (e.name === 'TimeoutError' || e.name === 'AbortError') {
      const err = new Error(
        'Không kết nối được API (hết thời gian chờ). Kiểm tra uvicorn tại cổng 8000.',
      )
      err.status = 0
      throw err
    }
    throw e
  }

  const text = await res.text()
  let data = null
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = { detail: text }
    }
  }

  if (!res.ok) {
    const err = new Error(formatDetail(data, res.status))
    err.status = res.status
    err.payload = data
    throw err
  }

  return data
}

function formatDetail(data, status) {
  if (!data) return `HTTP ${status}`
  const detail = data.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => item.msg || JSON.stringify(item))
      .join('; ')
  }
  return `HTTP ${status}`
}

export const api = {
  health: () => request('/', { timeoutMs: 3500 }),
  createSupplier: (body) => request('/suppliers', { method: 'POST', body }),
  createProject: (body) => request('/projects', { method: 'POST', body }),
  createBid: (body) => request('/bids', { method: 'POST', body }),
  evaluateProject: (projectId) =>
    request(`/projects/${projectId}/evaluate`, { method: 'POST' }),
  getDecision: (projectId) => request(`/projects/${projectId}/decision`),
}
