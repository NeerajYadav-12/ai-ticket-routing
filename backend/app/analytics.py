import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import func, text as sa_text
from sqlalchemy.orm import Session

from .db import get_db
from .models import Ticket, Assignment, ClassificationEvent
from .routing.engine import agent_open_tickets

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    by_topic = dict(db.query(Ticket.topic, func.count()).group_by(Ticket.topic).all())
    by_urgency = dict(db.query(Ticket.urgency, func.count()).group_by(Ticket.urgency).all())
    by_priority = {str(k): v for k, v in db.query(Ticket.priority, func.count()).group_by(Ticket.priority).all()}
    total = db.query(Ticket).count()
    resolved = db.query(Ticket).filter(Ticket.status == "resolved").count()
    open_ = db.query(Ticket).filter(Ticket.status != "resolved").count()

    avg_res = db.query(
        func.avg(func.timestampdiff(sa_text("HOUR"), Ticket.created_at, Ticket.resolved_at))
    ).filter(Ticket.resolved_at != None).scalar()  # noqa: E711

    return {
        "total": total,
        "open": open_,
        "resolved": resolved,
        "avg_resolution_hours": round(float(avg_res), 1) if avg_res is not None else None,
        "by_topic": by_topic,
        "by_urgency": by_urgency,
        "by_priority": by_priority,
    }


@router.get("/agents")
def agents(db: Session = Depends(get_db)):
    from .models import Agent
    out = []
    for a in db.query(Agent).all():
        avg_res = (
            db.query(func.avg(func.timestampdiff(sa_text("HOUR"), Ticket.created_at, Ticket.resolved_at)))
            .filter(Ticket.assigned_agent_id == a.id, Ticket.resolved_at != None).scalar()  # noqa: E711
        )
        out.append({
            "id": a.id, "name": a.name, "team": a.team.name if a.team else None,
            "expertise": a.expertise or [], "capacity": a.capacity,
            "open_tickets": agent_open_tickets(db, a.id),
            "resolved_total": db.query(Ticket).filter(
                Ticket.assigned_agent_id == a.id, Ticket.status == "resolved").count(),
            "avg_resolution_hours": round(float(avg_res), 1) if avg_res is not None else None,
        })
    return out


@router.get("/routing")
def routing(db: Session = Depends(get_db)):
    total_assignments = db.query(Assignment).count()
    auto = db.query(Assignment).filter(Assignment.auto == True).count()  # noqa: E712
    manual = total_assignments - auto
    tickets = db.query(Ticket).count()
    overridden = db.query(Ticket).filter(Ticket.manual_override == True).count()  # noqa: E712
    unassigned = db.query(Ticket).filter(Ticket.status == "new").count()
    reassignments = (
        db.query(func.count()).select_from(Assignment)
        .group_by(Assignment.ticket_id).having(func.count() > 1).count()
    )
    avg_latency = db.query(func.avg(ClassificationEvent.latency_ms)).scalar()
    return {
        "auto_assigned": auto,
        "manual_overrides": manual,
        "auto_pct": round(100 * auto / total_assignments) if total_assignments else 0,
        "override_pct": round(100 * overridden / tickets) if tickets else 0,
        "reassignments": reassignments,
        "unassigned": unassigned,
        "avg_latency_ms": round(float(avg_latency), 1) if avg_latency is not None else 0,
    }

