---
description: Create a new inbox action (email-triggered agent) via interactive wizard
---

# /chief-of-staff:create-inbox-action

Interactive wizard to create a new inbox action — an email-triggered agent that automatically processes specific types of emails (invoices, statements, notifications).

## What It Creates

- Agent file (`agents/inbox-action-{name}.md`)
- Command file (`commands/{command-name}.md`)
- Email route entry in `email-action-routes.yaml`
- Capabilities documentation in SKILL.md
- Optional: PDF extraction script, YNAB settings, skill docs

## Implementation

Delegate to the inbox action creator wizard agent:

```
Task:
  subagent_type: "chief-of-staff:inbox-action-creator"
  prompt: |
    Run the inbox action creator wizard.
    Guide the user through all steps to create a new email-triggered agent.
    Arguments: {{ ARGUMENTS }}
```
