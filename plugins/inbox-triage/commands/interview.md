---
description: Interactive voice-friendly inbox triage with questions-first flow and learning
argument-hint: "[--resume | --fresh]"
---

# /inbox-triage:interview

Fast, voice-friendly inbox triage that collects ALL decisions first (rapid Q&A), then executes in bulk, then learns from your choices.

## Usage

```
/inbox-triage:interview           # Start new or resume existing session
/inbox-triage:interview --resume  # Explicitly resume previous session
/inbox-triage:interview --fresh   # Start fresh (ignore previous session)
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

After answering all questions:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All 15 decisions collected!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
- Archive: 8 emails
- Delete: 4 emails
- Reminder: 2 emails
- Keep: 1 email

Ready to execute? (y/n)
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

## Learning

After each session, the system learns from your decisions:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Learning from your decisions...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Suggestion accuracy: 12/15 (80%)

Confidence updates:
  ↑ chase.com → Financial (+5%)
  ↑ amazon.com → Orders (+5%)
  ↓ newsletters.example.com (-15%)

New pattern detected:
  → bestbuy.com → Orders (add rule? y/n)
```

**How learning works:**
- Accepted suggestions boost confidence (+5%)
- Rejected suggestions lower confidence (-15%)
- Repeated patterns become new rules (after 3+ occurrences)
- Low-performing rules get flagged for review

## Prerequisites

1. Run `/inbox-triage:setup` to configure email provider
2. Run `/inbox-triage:learn` to bootstrap filing rules (optional but recommended)

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

Progress saved to `interview-state.yaml` after EVERY decision:
- Interrupt anytime by saying "stop" or "done"
- Resume later with `/inbox-triage:interview --resume`
- Start fresh with `/inbox-triage:interview --fresh`

Resume scenarios:
- **Mid-collection**: Continues from where you left off
- **Ready for execution**: Offers to execute collected decisions

## Final Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Emails archived: 8
Emails deleted: 4
Packages added: 2
Reminders created: 2
Newsletters unsubscribed: 1
Kept in inbox: 1

Learning:
- Suggestion accuracy: 80%
- Rules updated: 2
- New patterns: 1
```

## Why Questions-First?

| Old Flow | New Flow |
|----------|----------|
| Ask → Execute → Wait → Ask | Ask → Ask → Ask → Execute all |
| Slow (API call per email) | Fast (bulk API calls) |
| No learning | Learns from every decision |
