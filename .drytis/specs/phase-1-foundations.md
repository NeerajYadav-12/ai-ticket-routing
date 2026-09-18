# Phase 1 — Foundations

## Goal
Project scaffold, DB schema, seed data, ticket CRUD API, Caddy routing so the app loads end-to-end.

## Files
- `backend/` — FastAPI app (`main.py`), SQLAlchemy models, Pydantic schemas, routers: tickets, agents, teams
- `backend/db.py`, `backend/models.py`, `backend/seed.py`
- `frontend/` — Vite + React scaffold
- Caddy: `/api` → :8000, `/` → :5173

## Schema
- `teams(id, name, description)`
- `agents(id, name, team_id, expertise JSON ["billing","bug",...], capacity int, active bool)`
- `tickets(id, subject, body, status enum(new,assigned,in_progress,resolved), topic, urgency enum(low,medium,high,critical), priority int 1-4, assigned_agent_id, created_at, resolved_at, manual_override bool)`
- `assignments(id, ticket_id, agent_id, assigned_at, reason text)`
- `classification_events(id, ticket_id, topic_scores JSON, urgency_scores JSON, provider, latency_ms, created_at)`

## Seed
~60 synthetic tickets across topics (billing, bug, feature_request, account, how_to, integration), 3 teams, 8 agents with expertise profiles and varied open workloads.

## API
- `POST /api/tickets`, `GET /api/tickets` (+filters), `GET/PATCH /api/tickets/{id}`
- `GET /api/agents`, `GET /api/teams`

## Acceptance Criteria
- [ ] Preview URL loads the React UI
- [ ] Submitting a ticket via the UI/API stores it and appears in the ticket list
- [ ] Agent roster and teams are visible via API with seeded expertise
