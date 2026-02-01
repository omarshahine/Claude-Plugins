---
description: Generate a summary of automated emails
argument-hint: "[--all]"
---

# /inbox-triage:digest

Generate a categorized digest of automated emails.

## Usage

```
/inbox-triage:digest      # Unread automated emails
/inbox-triage:digest --all # Include read (last 24h)
```

## Implementation

Launch the `digest-generator` agent:

```
subagent_type: "inbox-triage:digest-generator"
prompt: "Generate digest of automated emails. Categorize and offer bulk actions."
```

## Categories

| Priority | Category |
|----------|----------|
| High | Security Alerts |
| High | Payment Issues |
| Medium | Account Issues |
| Low | Social |
| Low | Marketing |
| Low | Receipts |
