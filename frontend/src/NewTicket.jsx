import { useState } from 'react'
import { api } from './api'

export default function NewTicket({ onCreated }) {
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if (!subject.trim()) return
    setBusy(true)
    try {
      const t = await api.createTicket(subject, body)
      setResult(t)
      setSubject(''); setBody('')
      onCreated && onCreated(t)
    } finally { setBusy(false) }
  }

  return (
    <form onSubmit={submit} style={{ maxWidth: 560 }}>
      <h3>Submit a ticket</h3>
      <p style={{ color: '#64748b', fontSize: 13 }}>
        The classifier will detect topic and urgency, score priority, and auto-assign the best agent.
      </p>
      <input value={subject} onChange={e => setSubject(e.target.value)} placeholder="Subject"
             style={{ width: '100%', padding: 8, marginBottom: 8, boxSizing: 'border-box' }} />
      <textarea value={body} onChange={e => setBody(e.target.value)} placeholder="Describe the issue…"
                rows={5} style={{ width: '100%', padding: 8, marginBottom: 8, boxSizing: 'border-box' }} />
      <button disabled={busy}>{busy ? 'Classifying & routing…' : 'Submit ticket'}</button>
      {result && (
        <div style={{ marginTop: 12, padding: 12, border: '1px solid #10b98155', background: '#ecfdf5', borderRadius: 8, fontSize: 13 }}>
          Routed as <b>{result.topic}</b> / <b>{result.urgency}</b> / <b>P{result.priority}</b> →
          assigned to <b>{result.assigned_agent}</b>
          <div style={{ color: '#64748b', marginTop: 4 }}>{result.assignment_reason}</div>
        </div>
      )}
    </form>
  )
}
