import json
import os
import time
import httpx
from .base import ClassifierProvider, ClassificationResult, TOPICS, URGENCIES

SYSTEM_PROMPT = (
    "You are a support ticket classifier. Given a ticket, respond with ONLY a JSON object: "
    '{"topic_scores": {<each topic>: 0..1}, "urgency_scores": {<each urgency>: 0..1}}. '
    f'Topics: {TOPICS}. Urgencies: {URGENCIES}. Scores are probabilities and each set should sum to ~1.'
)


class OpenAIProvider(ClassifierProvider):
    name = "openai"

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("CLASSIFIER_MODEL", "gpt-4o-mini")

    async def classify(self, subject: str, body: str) -> ClassificationResult:
        started = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Subject: {subject}\n\nBody: {body[:2000]}"},
                    ],
                    "temperature": 0,
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
        topic_scores = {t: float(data.get("topic_scores", {}).get(t, 0)) for t in TOPICS}
        urgency_scores = {u: float(data.get("urgency_scores", {}).get(u, 0)) for u in URGENCIES}
        latency = (time.time() - started) * 1000
        return ClassificationResult(
            topic_scores=topic_scores,
            urgency_scores=urgency_scores,
            topic=max(topic_scores, key=topic_scores.get),
            urgency=max(urgency_scores, key=urgency_scores.get),
            provider=self.name,
            latency_ms=round(latency, 2),
        )
