"""Idempotent seeder: teams, agents, ~60 synthetic tickets."""
import random
import datetime
from .db import SessionLocal
from .models import Team, Agent, Ticket
from .scoring import compute_priority

random.seed(42)

TEAMS = [
    ("Billing", "Payments, invoices, refunds"),
    ("Technical Support", "Bugs, outages, integrations"),
    ("Customer Success", "Onboarding, how-to questions"),
]
AGENTS = [
    ("Priya Sharma", "Billing", ["billing", "account"], 6),
    ("Marcus Lee", "Billing", ["billing"], 4),
    ("Elena Petrova", "Technical Support", ["bug", "integration"], 5),
    ("David Kim", "Technical Support", ["bug", "how_to"], 5),
    ("Sofia Rossi", "Technical Support", ["integration"], 4),
    ("James Carter", "Customer Success", ["how_to", "feature_request"], 6),
    ("Amina Diallo", "Customer Success", ["account", "how_to"], 5),
    ("Tom Novak", "Customer Success", ["feature_request", "account"], 4),
]

SAMPLES = [
    ("billing", 'I was charged twice on invoice #{n} this month. Please refund the duplicate payment.', ["high", "medium"]),
    ("billing", 'My credit card was declined but the subscription shows active. Can you check the payment?', ["medium"]),
    ("billing", 'Can I get a receipt for the September invoice for our accounting team?', ["low"]),
    ("billing", 'We need to upgrade our plan but keep the annual pricing. How does billing handle that?', ["medium"]),
    ("bug", 'The dashboard throws a 500 error when I open the reports page. This is blocking our team.', ["high", "critical"]),
    ("bug", 'App crashes on startup since the latest update on Android.', ["medium", "high"]),
    ("bug", 'Export to CSV is producing corrupted files with broken columns.', ["medium"]),
    ("feature_request", 'It would be great if you could add Slack notifications for completed tasks.', ["low"]),
    ("feature_request", 'Please add dark mode to the mobile app — many of us work at night.', ["low"]),
    ("account", "I cannot log in to my account since yesterday. Password reset email never arrives.", ["high", "critical"]),
    ("account", 'How do I enable 2FA for all users in our organization?', ["medium"]),
    ("how_to", 'How do I set up recurring reports for my team? I could not find it in the documentation.', ["low"]),
    ("how_to", "Where can I find the API usage statistics for our workspace?", ["low", "medium"]),
    ("integration", "Our Zapier webhook stopped firing after your API change last week. Production workflows are affected.", ["high", "critical"]),
    ("integration", 'Can you share the OAuth scopes needed for the calendar sync integration?', ["medium", "low"]),
]

URGENCY_MAP = {"low": "low", "medium": "medium", "high": "high", "critical": "critical"}


def run():
    db = SessionLocal()
    if db.query(Ticket).count() > 0:
        print("Seed skipped: tickets already exist")
        db.close()
        return
    team_map = {}
    for name, desc in TEAMS:
        t = Team(name=name, description=desc)
        db.add(t)
        db.flush()
        team_map[name] = t.id
    agent_map = {}
    for name, team, expertise, capacity in AGENTS:
        a = Agent(name=name, team_id=team_map[team], expertise=expertise, capacity=capacity)
        db.add(a)
        db.flush()
        agent_map[name] = a.id

    tickets = []
    for topic, template, urgencies in SAMPLES:
        for i in range(4):
            u = random.choice(urgencies)
            subject = template.format(n=random.randint(10000, 99999)).split(".")[0][:120]
            tickets.append((subject, template.format(n=random.randint(10000, 99999)), topic, u))

    now = datetime.datetime.utcnow()
    for subject, body, topic, urgency in tickets:
        created = now - datetime.timedelta(hours=random.uniform(0.5, 72))
        t = Ticket(subject=subject, body=body, topic=topic, urgency=urgency,
                   priority=compute_priority(urgency, topic),
                   status=random.choices(["assigned", "in_progress", "resolved"], weights=[5, 3, 4])[0],
                   created_at=created)
        if t.status == "resolved":
            t.resolved_at = created + datetime.timedelta(hours=random.uniform(0.5, 20))
        db.add(t)
    db.commit()

    # assign most tickets round-robin-ish
    agent_ids = list(agent_map.values())
    open_tickets = db.query(Ticket).filter(Ticket.status.in_(["assigned", "in_progress"])).all()
    for i, t in enumerate(open_tickets):
        t.assigned_agent_id = agent_ids[i % len(agent_ids)]
    db.commit()
    print(f"Seeded {len(TEAMS)} teams, {len(AGENTS)} agents, {db.query(Ticket).count()} tickets")
    db.close()


if __name__ == "__main__":
    run()
