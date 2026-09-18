import { useEffect, useState } from 'react'
import { api } from './api'
import { TOPICS, URGENCIES, STATUSES, URGENCY_COLORS, PRIORITY_COLORS, STATUS_COLORS, Badge } from './ui'

export default function Queue({ refreshKey }) {
  const [tickets, setTickets] = useState([])
  const [agents, setAgents] = useState([])
  const [filters, setFilters] = useState({ topic: '', status: '', priority: '' })
  const [selected, setSelected] = useState(null)
  const [detail, setDetail] = useState(null)

  useEffect(() => { api.tickets(filters).then(setTickets).catch(console.error) }, [filters, refreshKey])
  useEffect(() => { api.agents().then(setAgents).catch(console.error) }, [])

  useEffect(() => {
    if (selected) api.ticket(selected).then(setDetail).catch(console.error)
    else setDetail(null)
  }, [selected, refreshKey])

  const act = async (fn) => {
    await fn()
    const t = await api.tickets(filters); setTickets(t)
    if (selected) setDetail(await api.ticket(selected))
  }

  return (
    <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
      <div style={{ flex: 2 }}>
        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
          <select value={filters.topic} onChange={e => setFilters({ ...filters, topic: e.target.value })}>
            <option value="">All topics</option>
            {TOPICS.map(t => <option key={t}>{t}</option>)}
          </select>
          <select value={filters.status} onChange={e => setFilters({ ...filters, status: e.target.value })}>
            <option value="">All statuses</option>
            {STATUSES.map(s => <option key={s}>{s}</option>)}
          </select>
          <select value={filters.priority} onChange={e => setFilters({ ...filters, priority: e.target.value })}>
            <option value="">All priorities</option>
            {[1, 2, 3, 4].map(p => <option key={p} value={p}>P{p}</option>)}
          </select>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ textAlign: 'left', color: '#64748b', borderBottom: '2px solid #e2e8f0' }}>
              <th style={{ padding: 6 }}>Subject</th><th>Topic</th><th>Urgency</th><th>Pri</th><th>Status</th><th>Agent</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map(t => (
              <tr key={t.id} onClick={() => setSelected(t.id)}
                  style={{ cursor: 'pointer', borderBottom: '1px solid #f1f5f9',
                           background: selected === t.id ? '#eff6ff' : undefined }}>
                <td style={{ padding: '6px 6px 6px 0', maxWidth: 320, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{t.subject}</td>
                <td>{t.topic}</td>
                <td><Badge color={URGENCY_COLORS[t.urgency]}>{t.urgency}</Badge></td>
                <td><Badge color={PRIORITY_COLORS[t.priority]}>P{t.priority}</Badge></td>
                <td><Badge color={STATUS_COLORS[t.status]}>{t.status}</Badge></td>
                <td>{t.assigned_agent || '—'}</td>
              </tr>
            ))}
            {tickets.length === 0 && <tr><td colSpan={6} style={{ padding: 20, color: '#94a3b8' }}>No tickets match the filters.</td></tr>}
          </tbody>
        </table>
      </div>
      {detail && (
        <div style={{ flex: 1, border: '1px solid #e2e8f0', borderRadius: 8, padding: 16, background: '#fff', position: 'sticky', top: 16 }}>
          <h3 style={{ margin: '0 0 8px', fontSize: 15 }}>#{detail.id} · {detail.subject}</h3>
          <p style={{ color: '#475569', fontSize: 13 }}>{detail.body}</p>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', margin: '10px 0' }}>
            <Badge color="#0ea5e9">{detail.topic}</Badge>
            <Badge color={URGENCY_COLORS[detail.urgency]}>{detail.urgency}</Badge>
            <Badge color={PRIORITY_COLORS[detail.priority]}>P{detail.priority}</Badge>
            <Badge color={STATUS_COLORS[detail.status]}>{detail.status}</Badge>
          </div>
          <p style={{ fontSize: 12, color: '#64748b' }}>
            Agent: <b>{detail.assigned_agent || 'unassigned'}</b>{detail.manual_override && ' (manual)'}<br />
            {detail.assignment_reason && <>Routing: {detail.assignment_reason}<br /></>}
            {detail.classification_provider && <>Classifier: {detail.classification_provider}</>}
          </p>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button onClick={() => act(() => api.reclassify(detail.id))}>Reclassify</button>
            <button onClick={() => act(() => api.reassign(detail.id))}>Auto-reassign</button>
            <select defaultValue="" onChange={e => e.target.value && act(() => api.patchTicket(detail.id, { assigned_agent_id: +e.target.value }))}>
              <option value="">Assign to…</option>
              {agents.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
            {detail.status !== 'resolved' && (
              <button onClick={() => act(() => api.patchTicket(detail.id, { status: 'resolved' }))}>Resolve</button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
