# Routing Regression Test Plan

Source ID: test-routing-regression

## Goal

Verify that inbound inquiries route to the correct queue with correct priority, assignment, tags, and SLA timer.

## Test Cases

1. Email inquiry with product tag routes to the matching product queue.
2. API-created inquiry with `queue_key` routes to the requested queue.
3. Disabled destination queue routes to fallback queue and adds `needs-triage`.
4. After-hours chat inquiry receives acknowledgement and keeps queue assignment.
5. Load balanced assignment chooses the available agent with the fewest open inquiries.

## Pass Criteria

All conversations show the expected queue in the audit log. SLA timers match the target queue policy within one minute.

## Regression Risk

Routing defects can create missed first-response SLAs, duplicate work, or lost escalation context.
