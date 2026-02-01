---
description: Process inbox emails with learned filing rules
argument-hint: "[--days N]"
---

# /inbox-triage:triage

Process inbox using learned rules. All suggestions require confirmation.

## Usage

```
/inbox-triage:triage          # New emails since last triage
/inbox-triage:triage --days 7 # Last 7 days
/inbox-triage:triage --all    # All inbox emails
```

## Prerequisites

1. Run `/inbox-triage:setup` first
2. Run `/inbox-triage:learn` to bootstrap rules

## Implementation

Launch the `inbox-triage` agent with the appropriate prompt:

**Default (new emails since last triage):**
```
subagent_type: "inbox-triage:inbox-triage"
prompt: "Process inbox emails since last triage. Match against rules, present suggestions for confirmation."
```

**With --days N:**
```
subagent_type: "inbox-triage:inbox-triage"
prompt: "Process inbox emails from the last N days. Match against rules, present suggestions for confirmation."
```

**With --all:**
```
subagent_type: "inbox-triage:inbox-triage"
prompt: "Process ALL inbox emails (ignore last triage date). Match against rules, present suggestions for confirmation."
```

## How Confidence Works

| Confidence | Meaning |
|------------|---------|
| 90%+ | Very reliable |
| 70-89% | Good match |
| <70% | Not suggested |

## Learning

| Action | Effect |
|--------|--------|
| Confirm | +5% confidence |
| Reject | -15% confidence |
| Correct | New rule created |
