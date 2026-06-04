# Queue SLA Rules

Source ID: ops-queue-sla-rules

## First Response Targets

- Priority urgent: 30 minutes during business hours.
- Priority high: 2 hours during business hours.
- Priority normal: 8 business hours.
- Priority low: 2 business days.

## State Effects

Open conversations count against response SLA. Waiting on engineering continues to require customer updates at the queue update cadence. Waiting on customer pauses the response timer only for queues that enable customer-wait pauses.

## Reopened Conversations

When a resolved conversation reopens, the response target is recalculated from the customer reply time. Reopened urgent inquiries should return to the front of the queue.

## Escalation

Any conversation within 15 minutes of breach should receive `sla-risk` and notify the queue lead.
