# Conversations API

Source ID: api-conversations
Base path: `/v1/conversations`

## Create Conversation

`POST /v1/conversations`

Creates a new customer inquiry. Use this endpoint when a product workflow needs to open a support conversation without email or widget input.

Required fields:

- `customer_id`
- `subject`
- `body`
- `channel`
- `idempotency_key`

Optional fields:

- `priority`
- `queue_key`
- `tags`
- `external_reference`

## Get Conversation

`GET /v1/conversations/{conversation_id}`

Returns conversation metadata, state, assigned agent, queue, messages, tags, and timestamps.

## Update State

`PATCH /v1/conversations/{conversation_id}/state`

Allowed states: `open`, `waiting_on_customer`, `waiting_on_engineering`, `resolved`.

## Idempotency

Use a stable idempotency key for retryable create requests. Duplicate keys return the original conversation ID with HTTP 200.
