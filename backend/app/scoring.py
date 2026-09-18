"""Priority scoring: urgency x topic impact, with SLA age escalation."""
from datetime import datetime, timedelta

URGENCY_WEIGHT = {"low": 1.0, "medium": 2.0, "high": 3.0, "critical": 4.0}
TOPIC_IMPACT = {
    "bug": 1.15,
    "billing": 1.1,
    "account": 1.05,
    "integration": 1.0,
    "how_to": 0.85,
    "feature_request": 0.8,
}
SLA_ESCALATION = timedelta(hours=2)


def compute_priority(urgency: str, topic: str) -> int:
    raw = URGENCY_WEIGHT.get(urgency, 2.0) * TOPIC_IMPACT.get(topic, 1.0)
    # map to P1..P4 (1 = highest)
    if raw >= 4.0:
        return 1
    if raw >= 2.8:
        return 2
    if raw >= 1.7:
        return 3
    return 4


def escalated_priority(priority: int, created_at: datetime, now: datetime | None = None) -> int:
    """Unassigned tickets older than the SLA window get bumped one level (P3→P2 etc.)."""
    now = now or datetime.utcnow()
    if priority > 1 and (now - created_at) > SLA_ESCALATION:
        return priority - 1
    return priority
