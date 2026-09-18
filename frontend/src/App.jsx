import { useEffect, useState } from 'react'
import Dashboard from './Dashboard'
import Queue from './Queue'
import NewTicket from './NewTicket'
import Agents from './Agents'

const TABS = { dashboard: 'Dashboard', queue: 'Ticket Queue', new: 'New Ticket', agents: 'Agents' }

export default function App() {
  const [tab, setTab] = useState('dashboard')
  const [refreshKey, setRefreshKey] = useState(0)
  const refresh = () => setRefreshKey(k => k + 1)

  // poll for new data every 15s
  useEffect(() => {
    const id = setInterval(refresh, 15000)
    return () => clearInterval(id)
  }, [])

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, sans-serif', background: '#f8fafc', minHeight: '100vh' }}>
      <header style={{ background: '#0f172a', color: '#fff', padding: '14px 24px', display: 'flex', alignItems: 'center', gap: 24 }}>
        <strong style={{ fontSize: 16 }}>🎫 AI Ticket Routing</strong>
        <nav style={{ display: 'flex', gap: 4 }}>
          {Object.entries(TABS).map(([k, label]) => (
            <button key={k} onClick={() => setTab(k)}
              style={{
                background: tab === k ? '#1e293b' : 'transparent', color: '#cbd5e1',
                border: 'none', padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontSize: 13,
              }}>{label}</button>
          ))}
        </nav>
      </header>
      <main style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
        {tab === 'dashboard' && <Dashboard refreshKey={refreshKey} />}
        {tab === 'queue' && <Queue refreshKey={refreshKey} />}
        {tab === 'new' && <NewTicket onCreated={refresh} />}
        {tab === 'agents' && <Agents />}
      </main>
    </div>
  )
}
