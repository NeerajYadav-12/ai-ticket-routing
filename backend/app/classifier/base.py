import time
from typing import Dict, List
from pydantic import BaseModel

TOPICS = ["billing", "bug", "feature_request", "account", "how_to", "integration"]
URGENCIES = ["low", "medium", "high", "critical"]


class ClassificationResult(BaseModel):
    topic_scores: Dict[str, float]
    urgency_scores: Dict[str, float]
    topic: str
    urgency: str
    provider: str
    latency_ms: float


class ClassifierProvider:
    name = "base"

    async def classify(self, subject: str, body: str) -> ClassificationResult:
        raise NotImplementedError
