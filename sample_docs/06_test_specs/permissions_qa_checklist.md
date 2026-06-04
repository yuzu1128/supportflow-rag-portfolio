# Permissions QA Checklist

Source ID: test-permissions-checklist

## Roles

- Agent can reply and assign but cannot export reports.
- Team Lead can approve macros and export permitted reports.
- Support Admin can manage users, queues, integrations, and API keys.
- Read Only Analyst can inspect conversations and export reports but cannot reply.

## Negative Tests

- Agent cannot rotate API keys.
- Read Only Analyst cannot change inquiry state.
- Team Lead cannot manage users unless also assigned Support Admin.
- Public export links do not include redacted token-like strings.

## Audit Expectations

Permission-denied events should include actor role, attempted action, target object type, and timestamp.
