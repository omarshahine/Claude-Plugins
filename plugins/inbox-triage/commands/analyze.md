---
description: Analyze Trash and Archive for organization insights
argument-hint: "[--trash | --archive]"
---

# /inbox-triage:analyze

Discover optimization opportunities from Trash and Archive patterns.

## Usage

```
/inbox-triage:analyze         # Both Trash and Archive
/inbox-triage:analyze --trash # Trash only (unsubscribe focus)
/inbox-triage:analyze --archive # Archive only (folder focus)
```

## Implementation

Launch the `organization-analyzer` agent:

```
subagent_type: "inbox-triage:organization-analyzer"
prompt: "Analyze Trash and Archive. Find unsubscribe candidates and misplaced emails."
```

## What It Finds

**From Trash:**
- Newsletters deleted without reading
- Delete patterns by category

**From Archive:**
- Emails that belong in existing folders
- Domains needing new folders
