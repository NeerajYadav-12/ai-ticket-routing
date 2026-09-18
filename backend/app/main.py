import datetime
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .db import get_db, Base, engine
from .models import Ticket, Agent, Team, ClassificationEvent
from .classifier.factory import get_provider
from .scoring import compute_priority
from .routing.engine import assign_ticket, agent_open_tickets
from .analytics import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging
    from sqlalchemy.exc import OperationalError
    log = logging.getLogger("startup")
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as e:
        # Two gunicorn workers may create tables concurrently (SQLite) —
        # "table already exists" is benign, the other worker won the race.
        if "already exists" in str(e):
            log.warning("Table creation raced with sibling worker; continuing: %s", e)
        else:
            raise
    yield

app = FastAPI(title="AI Ticket Routing API", lifespan=lifespan)

import os as _os
_origins = [o.strip() for o in _os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()] or ["*"]
app.add_middleware(CORSMiddleware, allow_origins=_origins, allow_methods=["*"], allow_headers=["*"])
app.include_router(analytics_router)


class TicketIn(BaseModel):
    subject: str
    body: str = ""


class TicketPatch(BaseModel):
    status: Optional[str] = None
    assigned_agent_id: Optional[int] = None


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/tickets")
async def create_ticket(data: TicketIn, db: Session = Depends(get_db)):
    ticket = Ticket(subject=data.subject, body=data.body, status="new")
    db.add(ticket)
    db.flush()

    provider = get_provider()
    result = await provider.classify(ticket.subject, ticket.body)
    ticket.topic = result.topic
    ticket.urgency = result.urgency
    ticket.priority = compute_priority(result.urgency, result.topic)
    db.add(ClassificationEvent(
        ticket_id=ticket.id, topic_scores=result.topic_scores,
        urgency_scores=result.urgency_scores, provider=result.provider,
        latency_ms=result.latency_ms,
    ))

    assignment = assign_ticket(db, ticket, auto=True)
    db.commit()
    db.refresh(ticket)
    return serialize_ticket(ticket, db, assignment_reason=assignment.reason)


@app.get("/api/tickets")
def list_tickets(topic: Optional[str] = None, status: Optional[str] = None,
                 priority: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(Ticket).order_by(Ticket.created_at.desc())
    if topic:
        q = q.filter(Ticket.topic == topic)
    if status:
        q = q.filter(Ticket.status == status)
    if priority:
        q = q.filter(Ticket.priority == priority)
    return [serialize_ticket(t, db) for t in q.limit(200)]


@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    t = db.query(Ticket).get(ticket_id)
    if not t:
        raise HTTPException(404)
    event = (db.query(ClassificationEvent)
             .filter(ClassificationEvent.ticket_id == ticket_id)
             .order_by(ClassificationEvent.created_at.desc()).first())
    return serialize_ticket(t, db, event=event)


@app.patch("/api/tickets/{ticket_id}")
def patch_ticket(ticket_id: int, data: TicketPatch, db: Session = Depends(get_db)):
    t = db.query(Ticket).get(ticket_id)
    if not t:
        raise HTTPException(404)
    if data.status:
        t.status = data.status
        if data.status == "resolved":
            t.resolved_at = datetime.datetime.utcnow()
    if data.assigned_agent_id is not None:
        assign_ticket(db, t, auto=False, forced_agent_id=data.assigned_agent_id)
    db.commit()
    db.refresh(t)
    return serialize_ticket(t, db)


@app.post("/api/tickets/{ticket_id}/reclassify")
async def reclassify(ticket_id: int, db: Session = Depends(get_db)):
    t = db.query(Ticket).get(ticket_id)
    if not t:
        raise HTTPException(404)
    provider = get_provider()
    result = await provider.classify(t.subject, t.body)
    t.topic = result.topic
    t.urgency = result.urgency
    t.priority = compute_priority(result.urgency, result.topic)
    db.add(ClassificationEvent(
        ticket_id=t.id, topic_scores=result.topic_scores,
        urgency_scores=result.urgency_scores, provider=result.provider,
        latency_ms=result.latency_ms,
    ))
    db.commit()
    db.refresh(t)
    return serialize_ticket(t, db)


@app.post("/api/tickets/{ticket_id}/reassign")
def reassign(ticket_id: int, db: Session = Depends(get_db)):
    t = db.query(Ticket).get(ticket_id)
    if not t:
        raise HTTPException(404)
    assignment = assign_ticket(db, t, auto=True)
    db.commit()
    db.refresh(t)
    return serialize_ticket(t, db, assignment_reason=assignment.reason)


@app.get("/api/agents")
def list_agents(db: Session = Depends(get_db)):
    out = []
    for a in db.query(Agent).all():
        out.append({
            "id": a.id, "name": a.name, "team_id": a.team_id,
            "team": a.team.name if a.team else None,
            "expertise": a.expertise or [], "capacity": a.capacity,
            "active": a.active, "open_tickets": agent_open_tickets(db, a.id),
        })
    return out


@app.get("/api/teams")
def list_teams(db: Session = Depends(get_db)):
    return [{"id": t.id, "name": t.name, "description": t.description} for t in db.query(Team).all()]


def serialize_ticket(t: Ticket, db: Session, assignment_reason: str | None = None,
                     event: ClassificationEvent | None = None):
    agent = db.query(Agent).get(t.assigned_agent_id) if t.assigned_agent_id else None
    return {
        "id": t.id, "subject": t.subject, "body": t.body, "status": t.status,
        "topic": t.topic, "urgency": t.urgency, "priority": t.priority,
        "assigned_agent_id": t.assigned_agent_id,
        "assigned_agent": agent.name if agent else None,
        "manual_override": t.manual_override,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "resolved_at": t.resolved_at.isoformat() if t.resolved_at else None,
        "assignment_reason": assignment_reason,
        "classification_provider": event.provider if event else None,
    }
