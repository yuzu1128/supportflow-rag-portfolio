# Incident Severity Policy

Source ID: incident-sev-policy
Owner: Support Operations

## Severity Levels

SEV1 means SupportFlow cannot receive, route, or display a broad set of customer inquiries. SEV1 requires executive notification, incident commander assignment, and customer status updates every 30 minutes.

SEV2 means a major workflow is degraded, such as delayed search indexing, webhook delivery failures, or one channel being unavailable. SEV2 requires updates every 60 minutes.

SEV3 means limited customer impact, degraded reporting, or a non-critical integration issue. SEV3 updates are posted when status changes.

## Roles

- Incident Commander: owns coordination and decision log.
- Support Lead: owns customer messaging and escalated conversation tagging.
- Engineering Lead: owns technical mitigation and rollback decision.
- Scribe: records timeline, impact, and follow-up actions.

## Required Tags

Use `incident-active`, `incident-sev1`, `incident-sev2`, or `incident-sev3` on affected conversations. Remove active tags only after the resolution notice is sent.
