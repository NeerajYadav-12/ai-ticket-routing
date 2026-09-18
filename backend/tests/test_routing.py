import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
from app.classifier.rule_provider import RuleBasedProvider
from app.scoring import compute_priority
from app.routing.engine import expertise_match, EXPERTISE_WEIGHT, LOAD_WEIGHT
from app.models import Agent


@pytest.mark.asyncio
async def test_outage_ticket_is_critical_bug():
    r = await RuleBasedProvider().classify("Urgent: production outage, all users affected", "Site is down, cannot work")
    assert r.topic in ("bug", "integration")
    assert r.urgency == "critical"
    assert compute_priority(r.urgency, r.topic) == 1


@pytest.mark.asyncio
async def test_billing_question():
    r = await RuleBasedProvider().classify("Charged twice on invoice", "Please refund the duplicate payment for invoice 12345")
    assert r.topic == "billing"
    assert compute_priority(r.urgency, "billing") >= 2


@pytest.mark.asyncio
async def test_casual_feature_request_is_low():
    r = await RuleBasedProvider().classify("Feature idea: dark mode", "Would be nice to have someday, no rush")
    assert r.topic == "feature_request"
    assert r.urgency == "low"


def test_priority_mapping():
    assert compute_priority("critical", "bug") == 1
    assert compute_priority("high", "billing") == 2
    assert compute_priority("medium", "how_to") == 3
    assert compute_priority("low", "feature_request") == 4


def test_expertise_match():
    a = Agent(id=1, name="x", expertise=["billing", "bug"], capacity=5)
    assert expertise_match(a, "billing") == 1.0
    assert expertise_match(a, "how_to") == 0.0
    g = Agent(id=2, name="g", expertise=[], capacity=5)
    assert expertise_match(g, "billing") == 0.5


def test_load_balancing_prefers_least_loaded():
    match = 1.0
    s_busy = EXPERTISE_WEIGHT * match + LOAD_WEIGHT * (1 - min(1, 5 / 5))
    s_free = EXPERTISE_WEIGHT * match + LOAD_WEIGHT * (1 - min(1, 1 / 5))
    assert s_free > s_busy
