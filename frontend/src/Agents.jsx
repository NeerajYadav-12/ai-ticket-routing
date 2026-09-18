import { useEffect, useState } from 'react'
import { api } from './api'
import { URGENCY_COLORS } from './ui'

export default function Agents() {
  const [agents, setAgents] = useState([])
  useEffect(() => { api.agents().then(setAgents) }, [])
  return (
    <div>
      <h3>Agent roster & load</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr style={{ textAlign: 'left', color: '#64748b', borderBottom: '2px solid #e2e8f0' }}>
            <th style={{ padding: 6 }}>Agent</th><th>Team</th><th>Expertise</th><th style={{ minWidth: 180 }}>Load</th>
          </tr>
        </thead>
        <tbody>
          {agents.map(a => {
            const ratio = Math.min(1, a.open_tickets / Math.max(1, a.capacity))
            const color = ratio >= 1 ? '#ef4444' : ratio >= 0.7 ? '#f97316' : '#10b981'
            return (
              <tr key={a.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                <td style={{ padding: 6 }}>{a.name}</td>
                <td>{a.team}</td>
                <td>{(a.expertise || []).join(', ')}</td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{ flex: 1, height: 8, background: '#f1f5f9', borderRadius: 4 }}>
                      <div style={{ width: `${ratio * 100}%`, height: '100%', background: color, borderRadius: 4 }} />
                    </div>
                    <span style={{ color, fontWeight: 600 }}>{a.open_tickets}/{a.capacity}</span>
                  </div>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
