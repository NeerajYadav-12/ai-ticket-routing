# Phase 4 — Routing Analytics Dashboard

## Goal
React dashboard visualizing routing performance and load.

## Files
- `backend/analytics.py` — endpoints: `/api/analytics/summary` (tickets by topic, urgency, priority, status), `/api/analytics/agents` (per-agent load, avg resolution time), `/api/analytics/routing` (assignments over time, avg classification latency, % auto vs manual, override rate)
- `frontend/` pages: Dashboard (summary cards + charts: topic distribution, priority mix, assignments over time), Queue (filterable ticket table with topic/urgency/priority badges, reclassify/reassign buttons), New Ticket form, Agents view (load bars)
- Recharts for all charts; polling (15s) for live-ish updates

## Edge Cases
- Empty DB → friendly empty states
- Long topic names truncated in charts

## Acceptance Criteria
- [ ] Dashboard shows ticket distribution by topic, urgency, and priority with charts
- [ ] Agent view shows per-agent open load vs capacity and average resolution time
- [ ] Routing stats show % auto-assigned, override rate, and avg classification latency
- [ ] Queue supports filtering by topic/priority/status and manual reassignment from UI
- [ ] Submitting a new ticket from the UI updates queue and dashboard within one refresh cycle
