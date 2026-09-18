# Phase 2 — Classification Engine + Priority Scoring

## Goal
Classify topic + urgency for every new ticket and compute a P1–P4 priority score.

## Files
- `backend/classifier/base.py` — abstract `ClassifierProvider` (`classify(subject, body) -> ClassificationResult{topic_scores, urgency, urgency_scores, provider, latency_ms}`)
- `backend/classifier/local_provider.py` — zero-shot `facebook/bart-large-mnli` (topic labels: billing, bug, feature_request, account, how_to, integration; urgency via NLI hypotheses + keyword boosters like "urgent", "production down", "cannot log in")
- `backend/classifier/openai_provider.py` — OpenAI-compatible chat API, JSON-output prompt, `OPENAI_BASE_URL`/`OPENAI_API_KEY`/`CLASSIFIER_MODEL` env
- `backend/classifier/factory.py` — chooses provider from `CLASSIFIER_PROVIDER=local|openai` env; falls back to rule-based if model unavailable
- `backend/scoring.py` — priority = urgency weight × topic impact weight, with SLA age escalation (ticket bumped one level if unassigned > 2h)
- Hook into `POST /api/tickets` and a `POST /api/tickets/{id}/reclassify` endpoint

## Edge Cases
- Provider down → rule-based keyword fallback, ticket still routed
- Latency logged to `classification_events` for analytics
- Empty/very short body → classified on subject alone

## Acceptance Criteria
- [ ] New ticket gets a topic, urgency, and P1–P4 priority automatically
- [ ] An obviously urgent ticket ("production down, all users affected") scores critical/P1
- [ ] Setting `CLASSIFIER_PROVIDER=openai` with a key routes classification through the external API with no code change
- [ ] Re-classifying an existing ticket updates topic/priority and logs an event
