---
description: Interactive voice-friendly inbox triage with questions-first flow
argument-hint: "[--resume | --fresh]"
---

# /chief-of-staff:triage

Fast, voice-friendly inbox triage that collects ALL decisions first (rapid Q&A), then executes in bulk, then learns from your choices.

## Usage

```
/chief-of-staff:triage           # Start new or resume existing session
/chief-of-staff:triage --resume  # Explicitly resume previous session
/chief-of-staff:triage --fresh   # Start fresh (ignore previous session)
```

## Three-Phase Flow

```
PHASE 1: COLLECT (fast Q&A)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Answer questions for each email
→ No waiting between emails
→ Decisions stored, not executed

PHASE 2: EXECUTE (bulk processing)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All actions run at once
→ Archive: single API call per folder
→ Delete: single API call for all
→ Sub-agents for parcel/reminders

PHASE 3: LEARN (improve suggestions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Record what you chose vs what we suggested
→ Update confidence scores
→ Detect new patterns
```

## How It Works

For each thread, you'll see:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Thread 3 of 15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

From:    Chase Bank <alerts@chase.com>
Subject: Your statement is ready

Summary: January statement available, balance due Feb 1.

Suggested: Archive to Financial (85% match)

1. Archive   2. Delete   3. Reminder   4. Keep

Say a number or action name.
```

## Voice-Friendly Options

| Say | Does |
|-----|------|
| 1, "archive", "file" | Move to a folder |
| 2, "delete", "trash" | Delete the email |
| 3, "reminder" | Create a reminder |
| 4, "keep", "skip", "next" | Keep in inbox |
| "parcel", "package" | Add to Parcel (when detected) |
| "unsubscribe" | Unsubscribe (for newsletters) |
| "stop", "done" | End collection, start execution |

## Smart Suggestions

Based on your filing rules and patterns:
- **Package emails**: "Add to Parcel (Recommended)"
- **Newsletters**: "Delete + Unsubscribe (Recommended)"
- **Filing matches**: "Archive to [Folder] (XX% match)"
- **Delete candidates**: "Delete (matches [pattern])"
- **Action items**: "Reminder (Recommended)"

## Prerequisites

1. Run `/chief-of-staff:setup` to configure email provider
2. Run `/chief-of-staff:learn` to bootstrap filing rules (optional but recommended)

## Implementation

Launch the `inbox-interviewer` agent:

**Default (new or resume):**
```
subagent_type: "chief-of-staff:inbox-interviewer"
prompt: "Start an interactive inbox interview. Check for existing session in interview-state.yaml and offer to resume if found."
```

**With --resume:**
```
subagent_type: "chief-of-staff:inbox-interviewer"
prompt: "Resume the previous inbox interview session from interview-state.yaml. Continue from where you left off."
```

**With --fresh:**
```
subagent_type: "chief-of-staff:inbox-interviewer"
prompt: "Start a fresh inbox interview session. Clear any existing interview-state.yaml and start from the beginning."
```
