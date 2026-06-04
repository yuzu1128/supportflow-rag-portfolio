# Queue Configuration Manual

Source ID: manual-queue-configuration
Audience: SupportFlow administrators

## Queue Types

SupportFlow uses queues to route inquiries by product area, customer segment, channel, and priority. A queue can receive messages from email, web widget, API-created conversations, and configured chat integrations.

## Required Fields

- Queue name
- Owner team
- Default priority
- Business hours calendar
- SLA policy
- Assignment method
- Fallback queue

## Assignment Methods

Round robin assigns the next inquiry to the next available agent. Load balanced assignment prefers the agent with the fewest open inquiries. Manual triage leaves the inquiry unassigned until a lead accepts or assigns it.

## Fallback Behavior

If no agent is available, the inquiry stays in the queue and the system adds the `needs-triage` tag. If a queue is disabled, new inbound inquiries are routed to the configured fallback queue.

## Recommended Defaults

Use load balanced assignment for production support queues. Use manual triage for engineering escalation queues. Use round robin for low-volume onboarding queues.
