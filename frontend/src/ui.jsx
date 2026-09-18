export const TOPICS = ['billing', 'bug', 'feature_request', 'account', 'how_to', 'integration']
export const URGENCIES = ['low', 'medium', 'high', 'critical']
export const STATUSES = ['new', 'assigned', 'in_progress', 'resolved']

export const URGENCY_COLORS = { low: '#10b981', medium: '#f59e0b', high: '#f97316', critical: '#ef4444' }
export const PRIORITY_COLORS = { 1: '#ef4444', 2: '#f97316', 3: '#f59e0b', 4: '#64748b' }
export const STATUS_COLORS = { new: '#3b82f6', assigned: '#8b5cf6', in_progress: '#f59e0b', resolved: '#10b981' }

export const Badge = ({ children, color }) => (
  <span style={{
    background: color + '22', color, border: `1px solid ${color}55`,
    padding: '1px 8px', borderRadius: 999, fontSize: 12, fontWeight: 600, whiteSpace: 'nowrap',
  }}>{children}</span>
)
