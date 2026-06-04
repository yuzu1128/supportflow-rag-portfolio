# Webhook Delivery Incident Runbook

Source ID: incident-webhook-runbook
Applies to: webhook event delivery, retry worker, customer callback endpoints

## Symptoms

- Customers report missing `conversation.created` or `conversation.updated` events.
- Webhook delivery dashboard shows retry backlog above 5,000 events.
- API consumers receive delayed automation triggers.

## Triage

1. Confirm whether event ingestion is healthy.
2. Check retry worker queue depth.
3. Compare failed callback status codes by customer endpoint.
4. Identify whether failures are global or limited to one destination domain.

## Mitigation

Pause low-priority replay jobs if retry workers are saturated. Increase retry worker concurrency only after confirming database write latency is normal. For customer endpoint failures, keep retries active and publish a targeted advisory.

## Customer Message

State that event delivery is delayed, not lost, unless engineering confirms data loss. Provide the affected event types and next update time.

## Resolution

Close the incident after backlog age is under 10 minutes for 30 consecutive minutes and replay verification passes.
