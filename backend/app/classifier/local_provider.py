"""Local zero-shot classification using a small NLI model.

Heavy transformers are an optional dependency — the import is lazy so the app
still boots (falling back to rules) if they aren't installed.
"""
import time
from .base import ClassifierProvider, ClassificationResult, TOPICS, URGENCIES

TOPIC_HYPOTHESES = {
    "billing": "This customer has a billing, invoice, payment or refund issue.",
    "bug": "This ticket reports something broken, an error or a malfunction.",
    "feature_request": "This customer is requesting a new feature or enhancement.",
    "account": "This ticket is about account access, login, password or profile.",
    "how_to": "This customer is asking how to do something or needs guidance.",
    "integration": "This ticket is about API, webhooks or third-party integrations.",
}
URGENCY_HYPOTHESES = {
    "low": "This is a casual question with no urgency.",
    "medium": "This is a normal support request that needs attention soon.",
    "high": "This is urgent and the customer is significantly blocked.",
    "critical": "This is critical: production is down and many users are affected.",
}


class LocalZeroShotProvider(ClassifierProvider):
    name = "local-zero-shot"

    def __init__(self):
        from transformers import pipeline  # lazy import
        self.pipe = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    async def classify(self, subject: str, body: str) -> ClassificationResult:
        started = time.time()
        text = f"{subject}. {body[:1500]}"
        t = self.pipe(text, list(TOPIC_HYPOTHESES.values()), multi_label=False)
        topic_scores = {
            topic: round(float(s), 3)
            for topic, s in zip([k for k in TOPIC_HYPOTHESES if TOPIC_HYPOTHESES[k] in t["labels"]], t["scores"])
        }
        u = self.pipe(text, list(URGENCY_HYPOTHESES.values()), multi_label=False)
        urgency_scores = {
            topic: round(float(s), 3)
            for topic, s in zip([k for k in URGENCY_HYPOTHESES if URGENCY_HYPOTHESES[k] in u["labels"]], u["scores"])
        }
        topic = max(topic_scores, key=topic_scores.get)
        urgency = max(urgency_scores, key=urgency_scores.get)
        latency = (time.time() - started) * 1000
        return ClassificationResult(
            topic_scores=topic_scores, urgency_scores=urgency_scores,
            topic=topic, urgency=urgency, provider=self.name, latency_ms=round(latency, 2),
        )
