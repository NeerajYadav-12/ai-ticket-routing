const BASE = import.meta.env.VITE_API_URL || ''

const json = async (r) => {
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`)
  return r.json()
}

export const api = {
  tickets: (filters = {}) => {
    const qs = new URLSearchParams(Object.entries(filters).filter(([, v]) => v))
    return fetch(`${BASE}/api/tickets?${qs}`).then(json)
  },
  ticket: (id) => fetch(`${BASE}/api/tickets/${id}`).then(json),
  createTicket: (subject, body) =>
    fetch(`${BASE}/api/tickets`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subject, body }),
    }).then(json),
  reclassify: (id) => fetch(`${BASE}/api/tickets/${id}/reclassify`, { method: 'POST' }).then(json),
  reassign: (id) => fetch(`${BASE}/api/tickets/${id}/reassign`, { method: 'POST' }).then(json),
  patchTicket: (id, data) =>
    fetch(`${BASE}/api/tickets/${id}`, {
      method: 'PATCH', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(json),
  agents: () => fetch(`${BASE}/api/agents`).then(json),
  teams: () => fetch(`${BASE}/api/teams`).then(json),
  analyticsSummary: () => fetch(`${BASE}/api/analytics/summary`).then(json),
  analyticsAgents: () => fetch(`${BASE}/api/analytics/agents`).then(json),
  analyticsRouting: () => fetch(`${BASE}/api/analytics/routing`).then(json),
}
