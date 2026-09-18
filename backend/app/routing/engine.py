"""Auto-assignment engine: expertise match x workload balancing."""
from sqlalchemy.orm import Session
from ..models import Agent, Ticket, Assignment

EXPERTISE_WEIGHT = 0.6
LOAD_WEIGHT = 0.4


def agent_open_tickets(db: Session, agent_id: int) -> int:
    return db.query(Ticket).filter(
        Ticket.assigned_agent_id == agent_id,
        Ticket.status.in_(["assigned", "in_progress"]),
    ).count()


def expertise_match(agent: Agent, topic: str) -> float:
    exp = agent.expertise or []
    if not exp:
        return 0.5  # neutral: generalist
    return 1.0 if topic in exp else 0.0


def score_agents(db: Session, agents: list[Agent], topic: str) -> dict[int, tuple[float, int, float]]:
    """Returns {agent_id: (score, open_count, expertise_match)}."""
    out = {}
    for a in agents:
        open_count = agent_open_tickets(db, a.id)
        match = expertise_match(a, topic)
        load_ratio = min(1.0, open_count / max(1, a.capacity or 1))
        score = EXPERTISE_WEIGHT * match + LOAD_WEIGHT * (1 - load_ratio)
        out[a.id] = (round(score, 4), open_count, match)
    return out


def pick_agent(db: Session, topic: str, urgency: str, allow_cross_team: bool = True):
    """Returns (agent, score, open_count, match, reason) or (None, 0, 0, 0, reason)."""
    q = db.query(Agent).filter(Agent.active == True)  # noqa: E712
    if not allow_cross_team and urgency != "critical":
        q = q.filter(Agent.expertise.contains(f'"{topic}"'))
    agents = q.all()
    if not agents:
        return None, 0, 0, 0.0, "no eligible agent"
    scored = score_agents(db, agents, topic)
    best_id = max(scored, key=lambda aid: (scored[aid][0], -aid))
    score, open_count, match = scored[best_id]
    best = next(a for a in agents if a.id == best_id)
    reason = f"expertise match {topic} ({match}), load {open_count}/{best.capacity}, score {score}"
    return best, score, open_count, match, reason


def assign_ticket(db: Session, ticket: Ticket, auto: bool = True,
                  forced_agent_id: int | None = None, reason: str = "") -> Assignment:
    if forced_agent_id:
        agent = db.query(Agent).get(forced_agent_id)
        assignment = Assignment(
            ticket_id=ticket.id, agent_id=forced_agent_id,
            reason=reason or "manual assignment", auto=False,
        )
        ticket.assigned_agent_id = forced_agent_id
        if not auto:
            ticket.manual_override = True
    else:
        agent, score, open_count, match, reason = pick_agent(db, ticket.topic or "", ticket.urgency or "")
        assignment = Assignment(
            ticket_id=ticket.id, agent_id=agent.id if agent else None,
            reason=reason, auto=True,
        )
        if agent:
            ticket.assigned_agent_id = agent.id
    if ticket.assigned_agent_id:
        ticket.status = "assigned"
    db.add(assignment)
    return assignment
