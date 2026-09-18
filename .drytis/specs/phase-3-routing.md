# Phase 3 — Auto-Assignment Engine

## Goal
Assign each classified ticket to the best agent balancing expertise match and workload.

## Files
- `backend/routing/engine.py` — score per active agent: `score = 0.6 × expertise_match(topic) + 0.4 × (1 − load_ratio)`, expertise_match = fraction of agent's expertise list matching topic (1.0 if exact), load_ratio = open tickets / capacity. Cross-team escalation allowed for critical tickets.
- `backend/routing/service.py` — assign on ticket creation (post-classification), `POST /api/tickets/{id}/reassign`, auto-reassign if priority escalates to P1 and current agent overloaded
- Writes `assignments` row with human-readable `reason` (e.g. "expertise match billing (1.0), load 2/5")
- Manual override: PATCH assigned_agent_id sets `manual_override=true`; engine never auto-reassigns overridden tickets

## Edge Cases
- No active agent → ticket stays `new` with `assignments` note "no eligible agent"
- Tie → lowest agent id (deterministic)

## Acceptance Criteria
- [ ] Creating a ticket auto-assigns it to an agent with matching expertise when one has capacity
- [ ] Workload balancing: with equal expertise, the least-loaded agent wins
- [ ] Assignment reason is stored and visible in API/ticket detail
- [ ] Manual reassignment sticks — engine does not override it
