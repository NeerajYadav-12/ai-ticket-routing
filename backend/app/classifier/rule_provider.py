import re
import time
from typing import Dict, List
from .base import ClassifierProvider, ClassificationResult, TOPICS, URGENCIES

URGENT_PATTERNS = [
    (r"production|outage|down|cannot log in|can't log in|all users affected|data loss|security breach", 0.6),
    (r"urgent|asap|immediately|critical|blocked|deadline", 0.3),
    (r"not working|broken|error|crash|failed|failing", 0.2),
    (r"whenever|sometime|feature request|suggestion|idea|question|how (do|to|can)", -0.3),
]


class RuleBasedProvider(ClassifierProvider):
    name = "rules"

    async def classify(self, subject: str, body: str) -> ClassificationResult:
        started = time.time()
        text = f"{subject} {body}".lower()
        topic_scores = self._score_topics(text)
        urgency_scores = self._score_urgency(text)
        topic = max(topic_scores, key=topic_scores.get)
        urgency = max(urgency_scores, key=urgency_scores.get)
        latency = (time.time() - started) * 1000
        return ClassificationResult(
            topic_scores=topic_scores, urgency_scores=urgency_scores,
            topic=topic, urgency=urgency, provider=self.name, latency_ms=round(latency, 2),
        )

    def _score_topics(self, text: str) -> Dict[str, float]:
        keywords = {
            "billing": [r"invoice", r"charge", r"refund", r"payment", r"billing", r"subscription", r"price", r"card", r"receipt"],
            "bug": [r"bug", r"error", r"crash", r"broken", r"not working", r"fails?", r"exception", r"500",
                    r"outage", r"down", r"affected", r"production", r"stopped", r"stopped working", r"data loss", r"degraded"],
            "feature_request": [r"feature", r"suggest", r"request", r"would be nice", r"enhancement", r"idea"],
            "account": [r"login", r"log in", r"password", r"account", r"sign ?up", r"sso", r"2fa", r"profile",
                        r"cannot access my", r"locked out"],
            "how_to": [r"how (do|to|can)", r"guide", r"documentation", r"tutorial", r"where (do|can)"],
            "integration": [r"api", r"webhook", r"integrat", r"zapier", r"slack", r"sync", r"oauth", r"endpoint"],
        }
        scores = {}
        for topic, pats in keywords.items():
            hits = sum(len(re.findall(p, text)) for p in pats)
            scores[topic] = min(1.0, 0.35 + hits * 0.2) if hits else 0.1
        total = sum(scores.values()) or 1
        return {k: round(v / total, 3) for k, v in scores.items()}

    def _score_urgency(self, text: str) -> Dict[str, float]:
        strong = any(re.search(p, text) for p, w in URGENT_PATTERNS if w >= 0.6)
        score = 0.35
        for pattern, weight in URGENT_PATTERNS:
            if re.search(pattern, text):
                if weight < 0 and strong:
                    continue  # a strong outage/login signal beats casual-question phrasing
                score += weight
        score = max(0.02, min(0.95, score))
        # spread across the 4 buckets, concentrated near `score`
        raw = {}
        for i, u in enumerate(URGENCIES):
            center = 0.2 + i * 0.25
            raw[u] = max(0.01, 1 - abs(score - center) * 6)
        total = sum(raw.values())
        return {k: round(v / total, 3) for k, v in raw.items()}
