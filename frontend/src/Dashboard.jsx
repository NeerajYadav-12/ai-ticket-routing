import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts'
import { api } from './api'
import { TOPICS, URGENCIES, URGENCY_COLORS, PRIORITY_COLORS, STATUS_COLORS } from './ui'

const Card = ({ title, value, sub }) => (
  <div style={{ flex: 1, border: '1px solid #e2e8f0', borderRadius: 8, padding: 16, background: '#fff', minWidth: 140 }}>
    <div style={{ color: '#64748b', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>{title}</div>
    <div style={{ fontSize: 28, fontWeight: 700, marginTop: 4 }}>{value}</div>
    {sub && <div style={{ color: '#94a3b8', fontSize: 12 }}>{sub}</div>}
  </div>
)

export default function Dashboard({ refreshKey }) {
  const [summary, setSummary] = useState(null)
  const [agents, setAgents] = useState([])
  const [routing, setRouting] = useState(null)

  useEffect(() => {
    api.analyticsSummary().then(setSummary).catch(console.error)
    api.analyticsAgents().then(setAgents).catch(console.error)
    api.analyticsRouting().then(setRouting).catch(console.error)
  }, [refreshKey])

  if (!summary) return <p style={{ color: '#94a3b8' }}>Loading analytics…</p>

  const dist = (counts, keys) => keys.map(k => ({ name: k, value: counts[k] || 0 })).filter(d => d.value > 0)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <Card title="Total tickets" value={summary.total} />
        <Card title="Open" value={summary.open} sub="new + assigned + in progress" />
        <Card title="Resolved" value={summary.resolved} />
        <Card title="Avg resolution" value={summary.avg_resolution_hours != null ? `${summary.avg_resolution_hours}h` : '—'} />
        <Card title="Classifier latency" value={routing ? `${routing.avg_latency_ms}ms` : '—'} sub="avg per classification" />
      </div>
      <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 300, border: '1px solid #e2e8f0', borderRadius: 8, padding: 16, background: '#fff' }}>
          <h4 style={{ margin: '0 0 8px' }}>Tickets by topic</h4>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={dist(summary.by_topic, TOPICS)} dataKey="value" nameKey="name" outerRadius={80} label>
                {dist(summary.by_topic, TOPICS).map((d, i) => (
                  <Cell key={d.name} fill={['#0ea5e9', '#ef4444', '#8b5cf6', '#f59e0b', '#10b981', '#f97316'][i % 6]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div style={{ flex: 1, minWidth: 300, border: '1px solid #e2e8f0', borderRadius: 8, padding: 16, background: '#fff' }}>
          <h4 style={{ margin: '0 0 8px' }}>By urgency & priority</h4>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={URGENCIES.map(u => ({ name: u, tickets: summary.by_urgency[u] || 0 }))}>
              <XAxis dataKey="name" /><YAxis allowDecimals={false} /><Tooltip />
              <Bar dataKey="tickets">{URGENCIES.map(u => <Cell key={u} fill={URGENCY_COLORS[u]} />)}</Bar>
            </BarChart>
          </ResponsiveContainer>
          <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
            {[1, 2, 3, 4].map(p => (
              <span key={p} style={{ fontSize: 12, color: PRIORITY_COLORS[p], fontWeight: 600 }}>
                P{p}: {summary.by_priority[p] || 0}
              </span>
            ))}
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 300, border: '1px solid #e2e8f0', borderRadius: 8, padding: 16, background: '#fff' }}>
          <h4 style={{ margin: '0 0 8px' }}>Agent load (open / capacity)</h4>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart layout="vertical" data={agents.map(a => ({ name: a.name, open: a.open_tickets, cap: a.capacity }))}>
              <XAxis type="number" allowDecimals={false} /><YAxis type="category" dataKey="name" width={110} /><Tooltip />
              <Legend />
              <Bar dataKey="open" name="Open" fill="#3b82f6" />
              <Bar dataKey="cap" name="Capacity" fill="#e2e8f0" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ flex: 1, minWidth: 300, border: '1px solid #e2e8f0', borderRadius: 8, padding: 16, background: '#fff' }}>
          <h4 style={{ margin: '0 0 8px' }}>Routing health</h4>
          {routing && (
            <ul style={{ fontSize: 13, lineHeight: 2, margin: 0, paddingLeft: 18 }}>
              <li>Auto-assigned: <b>{routing.auto_assigned}</b> ({routing.auto_pct}%)</li>
              <li>Manual overrides: <b>{routing.manual_overrides}</b> ({routing.override_pct}%)</li>
              <li>Reassignments: <b>{routing.reassignments}</b></li>
              <li>Unassigned (no eligible agent): <b>{routing.unassigned}</b></li>
              <li>Avg classification latency: <b>{routing.avg_latency_ms}ms</b></li>
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}
