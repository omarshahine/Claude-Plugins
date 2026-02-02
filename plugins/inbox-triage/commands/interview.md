---
description: Interactive voice-friendly inbox triage - process emails one by one
argument-hint: "[--resume | --fresh]"
---

# /inbox-triage:interview

Interactive voice-friendly inbox triage that processes emails one-by-one with simple numbered questions.

## Usage

```
/inbox-triage:interview           # Start new or resume existing session
/inbox-triage:interview --resume  # Explicitly resume previous session
/inbox-triage:interview --fresh   # Start fresh (ignore previous session)
```

## Prerequisites

1. Run `/inbox-triage:setup` to configure email provider
2. Run `/inbox-triage:learn` to bootstrap filing rules (optional but recommended)

## How It Works

For each email, you'll see:
```
Email 3 of 15 from Chase Bank:
"Your statement is ready"

This looks like a financial alert.
1. Reminder   2. Calendar   3. Archive
4. Delete     5. Keep       6. Reply

Say a number or action name.
```

Just say a number (1-6) or action name (reminder, calendar, archive, delete, keep, reply).

## Voice-Friendly Options

| Say | Does |
|-----|------|
| 1, "reminder" | Create a reminder |
| 2, "calendar" | Create a calendar event |
| 3, "archive", "file" | Move to a folder |
| 4, "delete", "trash" | Delete the email |
| 5, "keep", "skip" | Keep in inbox |
| 6, "reply", "respond" | Draft a reply |
| "stop", "done" | End session |

## Smart Suggestions

The interview uses your existing triage patterns to suggest actions:
- **Package emails**: Detected using shipping patterns
- **Newsletters**: Detected using newsletter patterns
- **Filing matches**: Suggested based on filing-rules.yaml
- **Delete candidates**: Detected using delete-patterns.yaml
- **Financial alerts**: Detected by sender domain
- **Action items**: Detected by keywords (please, due, deadline, etc.)

## Implementation

Launch the `inbox-interviewer` agent:

**Default (new or resume):**
```
subagent_type: "inbox-triage:inbox-interviewer"
prompt: "Start an interactive inbox interview. Check for existing session in interview-state.yaml and offer to resume if found."
```

**With --resume:**
```
subagent_type: "inbox-triage:inbox-interviewer"
prompt: "Resume the previous inbox interview session from interview-state.yaml. Continue from where you left off."
```

**With --fresh:**
```
subagent_type: "inbox-triage:inbox-interviewer"
prompt: "Start a fresh inbox interview session. Clear any existing interview-state.yaml and start from the beginning."
```

## Session State

Progress is automatically saved to `interview-state.yaml`, so you can:
- Interrupt anytime by saying "stop" or "done"
- Resume later with `/inbox-triage:interview --resume`
- Start fresh with `/inbox-triage:interview --fresh`

## Summary

At the end of each session, you'll see:
```
Session complete!

Summary:
- Reminders created: 3
- Calendar events: 1
- Emails archived: 8
- Emails deleted: 2
- Kept in inbox: 1
- Replies drafted: 0
```
