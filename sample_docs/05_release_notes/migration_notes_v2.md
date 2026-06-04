# Migration Notes: SupportFlow API v2 Preview

Source ID: release-migration-v2

## Scope

API v2 preview introduces cursor pagination, normalized message visibility values, and stricter validation for conversation state changes.

## Breaking Preview Changes

- `messages[].is_internal` is replaced by `messages[].visibility`.
- Pagination uses `next_cursor` instead of page numbers.
- Invalid state transitions return `VALIDATION_422`.

## Recommended Migration

1. Update webhook consumers to read `visibility`.
2. Add cursor pagination support.
3. Validate state transitions before calling the API.
4. Keep v1 idempotency behavior for create conversation workflows.

## Not Changing

API keys, rate limit headers, webhook signature header, and event names remain unchanged in the preview.
