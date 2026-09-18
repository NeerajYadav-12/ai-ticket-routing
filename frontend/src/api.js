const json = async (r) => {
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`)
  return r.json()
}

export const api = {
  tickets: (filters = {}) => {
    const qs = new URLSearchParams(Object.entries(filters).filter(([, v]) => v))
    return fetch(`/api/tickets?${qs}`).then(json)
  },
  ticket: (id) => fetch(`/api/tickets/${id}`).then(json),
  createTicket: (subject, body) =>
    fetch('/api/tickets', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subject, body }),
    }).then(json),
  reclassify: (id) => fetch(`/api/tickets/${id}/reclassify`, { method: 'POST' }).then(json),
  reassign: (id) => fetch(`/api/tickets/${id}/reassign`, { method: 'POST' }).then(json),
  patchTicket: (id, data) =>
    fetch(`/api/tickets/${id}`, {
      method: 'PATCH', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(json),
  agents: () => fetch('/api/agents').then(json),
  teams: () => fetch('/api/teams').then(json),
  analyticsSummary: () => fetch('/api/analytics/summary').then(json),
  analyticsAgents: () => fetch('/api/analytics/agents').then(json),
  analyticsRouting: () => fetch('/api/analytics/routing').then(json),
}
