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
| 5, "flag" | Flag for follow-up (contextual) |
| "parcel", "package" | Add to Parcel (when detected) |
| "unsubscribe" | Unsubscribe (for newsletters) |
| "stop", "done" | End collection, start execution |

## Smart Suggestions

Based on your filing rules and patterns:
- **Package emails**: "Add to Parcel (Recommended)"
- **Newsletters**: "Delete + Unsubscribe (Recommended)"
- **Filing matches**: "Archive to [Folder] (XX% match)"
- **Delete candidates**: "Delete (matches [pattern])"
- **Action items**: "Flag (Recommended)" or "Reminder (Recommended)"

### Contextual Flag Option

The **Flag** option appears ONLY when the email signals action is needed. Do NOT show Flag on every email — it replaces one of the standard 4 options when contextually appropriate.

**Show Flag when ANY of these are true:**
- Subject contains "ACTION REQUIRED", "action needed", "please review", "please sign", "response needed", "RSVP"
- Email is a direct personal reply expecting a response (someone asking a question)
- Email contains a deadline or due date in the preview
- Email is from a known contact and appears to be a conversation awaiting your input
- Subject contains "Re:" and the sender is asking a question or requesting something

**Do NOT show Flag when:**
- Email is a newsletter, marketing, or automated notification
- Email is a shipping/order confirmation
- Email is a calendar invite or acceptance/decline
- Email is spam or clearly deletable
- Email is informational with no action needed

## Prerequisites

1. Run `/chief-of-staff:setup` to configure email provider
2. Run `/chief-of-staff:learn` to bootstrap filing rules (optional but recommended)

## Implementation

**IMPORTANT: Run directly in main agent, NOT as a sub-agent.**

Sub-agents spawned via Task tool do NOT have access to `AskUserQuestion`. The triage workflow requires AskUserQuestion for interactive email decisions, so it MUST run in the main agent context.

**Workflow:**

1. **Load context BEFORE presenting emails:**
   a. Read `~/.claude/data/chief-of-staff/settings.yaml` to get `EMAIL_PROVIDER` and `EMAIL_TOOLS` mappings
   b. Load email MCP tools via ToolSearch (`+{EMAIL_PROVIDER}`, e.g. `+fastmail`)
   c. Load Parcel MCP tools via ToolSearch (`+parcel deliveries`)
   d. Read `~/.claude/data/chief-of-staff/filing-rules.yaml` for filing suggestions
   e. Read `~/.claude/data/chief-of-staff/delete-patterns.yaml` for delete suggestions
   f. Fetch current Parcel deliveries via Parcel `get_deliveries` (include_delivered: true)
   g. Fetch inbox emails with `EMAIL_TOOLS.list_emails` (limit: 50) using the Inbox mailbox ID

2. **PHASE 1 - COLLECT:** For each email, use `AskUserQuestion` to present options:
   - Include email summary in the question text
   - Provide up to 4 options from the contextual set (AskUserQuestion max is 4 options)
   - **Base options** (always available): Archive, Delete, Keep
   - **Contextual options** (replace one base option when relevant):
     - **Flag**: Show when email signals action needed (see "Contextual Flag Option" above). Replaces Reminder or Keep depending on context.
     - **Reminder**: Show when there's a specific deadline or timed follow-up
     - **Unsubscribe + Delete**: Show for newsletters with `$canunsubscribe` keyword
     - **Add to Parcel + Archive**: Show for untracked shipping emails
   - For shipping emails: cross-reference Parcel deliveries. If already tracked, note "Already in Parcel" and suggest "Archive to Orders". If not tracked, offer "Add to Parcel + Archive"
   - For emails matching delete patterns: show "(Recommended)" with pattern match note
   - For emails matching filing rules: show folder suggestion with confidence

3. **PHASE 2 - EXECUTE:** Collect all decisions, then execute in this order:
   a. **Unsubscribes FIRST** - Delegate to `chief-of-staff:newsletter-unsubscriber` sub-agent
      (must happen before delete so emails are still accessible)
   b. **Parcel tracking** - Delegate to `chief-of-staff:inbox-to-parcel` sub-agent
   c. **Reminders** - Create via `mcp__apple-pim__reminder_create`
   d. **Flags** - `EMAIL_TOOLS.bulk_flag` for all flagged emails (keeps in inbox, marks for follow-up)
   e. **Archives** - `EMAIL_TOOLS.bulk_move` grouped by folder
   f. **Deletes** - `EMAIL_TOOLS.bulk_delete` for all deletions (including unsubscribed emails)

4. **PHASE 3 - LEARN (mandatory):** After execution, update data files:
   a. **decision-history.yaml** - Append ALL decisions with: date, emailId, action, senderDomain, senderEmail (if available), folder (if archived), category, accepted (true if user followed the system suggestion, false if user chose a different action), and notes for pattern matches
   b. **delete-patterns.yaml** - Bump `match_count` for any confirmed delete patterns. For new domains deleted 2+ times in this session, add as new patterns with confidence 0.75 and source "triage"
   c. **Update statistics** - Increment total_decisions, by_action counts, total_sessions
   d. Report summary

**IMPORTANT: Unsubscribes must run BEFORE deletes.** The unsubscriber needs to fetch email content to find unsubscribe links. If emails are deleted first, the links are lost.

**IMPORTANT: Phase 3 (LEARN) is NOT optional.** Every triage session must persist decisions to data files. This is how the system improves suggestions over time.

**Question format:**
```
AskUserQuestion:
  questions:
    - question: "Email X/Y: '[Subject]' from [Sender] - [Brief summary of content]"
      header: "Email X/Y"
      multiSelect: false
      options:
        - label: "[Recommended action]"
          description: "[Why recommended]"
        - label: "Archive"
          description: "Move to a folder"
        - label: "Delete"
          description: "Delete this email"
        - label: "Keep"
          description: "Leave in inbox"
```

**Reference:** See `agents/inbox-interviewer.md` for detailed workflow, smart suggestions, and follow-up question patterns.
