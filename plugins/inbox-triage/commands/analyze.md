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

Launch the `organization-analyzer` agent with the appropriate prompt:

**Default (both Trash and Archive):**
```
subagent_type: "inbox-triage:organization-analyzer"
prompt: "Analyze both Trash and Archive. Find unsubscribe candidates in Trash and misplaced emails in Archive."
```

**With --trash:**
```
subagent_type: "inbox-triage:organization-analyzer"
prompt: "Analyze Trash only. Focus on finding unsubscribe candidates and delete patterns."
```

**With --archive:**
```
subagent_type: "inbox-triage:organization-analyzer"
prompt: "Analyze Archive only. Focus on finding misplaced emails and new folder opportunities."
```

## What It Finds

**From Trash:**
- Newsletters deleted without reading
- Delete patterns by category

**From Archive:**
- Emails that belong in existing folders
- Domains needing new folders
