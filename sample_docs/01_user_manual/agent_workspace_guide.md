# Agent Workspace Guide

Source ID: manual-agent-workspace
Audience: SupportFlow agents and team leads

## Purpose

The Agent Workspace is the primary screen for handling customer inquiries. It combines the conversation timeline, customer profile, assignment panel, response composer, internal notes, and knowledge suggestions.

## Core Workflow

1. Open the assigned queue from the left navigation.
2. Select the oldest inquiry with a visible SLA timer.
3. Review the customer profile, plan, tags, and previous conversations.
4. Check the suggested articles before drafting a response.
5. Add an internal note when the next agent needs context.
6. Send the response or change the inquiry state.

## Inquiry States

- New: received but not accepted by an agent.
- Open: accepted and actively being handled.
- Waiting on customer: the agent asked for more information.
- Waiting on engineering: escalation is active and engineering owns the next technical update.
- Resolved: customer-facing answer was sent and no further action is expected.
- Reopened: customer replied after resolution.

## Composer Rules

Use public replies for customer-visible messages. Use internal notes for investigation details, API payloads, logs, and escalation summaries. Never paste credentials, session tokens, or private customer data into a public reply.

## Workspace Hints

The SLA timer is based on queue policy, priority, and business-hours settings. Changing priority can recalculate the timer. Suggested articles are ranked by subject, tags, product area, and customer plan.
