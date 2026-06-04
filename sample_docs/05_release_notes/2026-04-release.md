# Release Notes: April 2026

Source ID: release-2026-04

## New

- Added `message.created` webhook event with visibility field.
- Added `waiting_on_engineering` as a public API state.
- Added macro variable validation before sending customer replies.

## Changed

Webhook signature documentation now requires verification against the raw request body. API examples now include `X-SupportFlow-Signature`.

## Fixed

- Fixed RATE_429 headers on burst-limited requests.
- Fixed article review filters for retired articles.
- Fixed assignment count drift after bulk reassignment.

## Rollout Note

Customers using webhook libraries must confirm raw-body access before enabling strict signature validation.
