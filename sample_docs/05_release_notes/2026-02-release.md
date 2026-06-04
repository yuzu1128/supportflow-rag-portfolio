# Release Notes: February 2026

Source ID: release-2026-02

## Highlights

- Added load balanced assignment for production support queues.
- Added queue-level fallback routing when a queue is disabled.
- Improved agent article suggestions with product-area metadata.

## Behavior Changes

Queue rename history now appears in conversation audit logs. Existing reports preserve historical queue names while new reports show the current queue name.

## Fixes

- Fixed an issue where internal note drafts could remain visible after switching conversations.
- Fixed a rare duplicate webhook event when conversation creation was retried without an idempotency key.

## Operational Notes

Support leads should review queue fallback settings after enabling load balanced assignment.
