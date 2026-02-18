---
description: Full daily orchestration routine
---

# /chief-of-staff:daily

Run the full daily Chief-of-Staff routine: status check, package processing, inbox triage, and digest.

## Usage

```
/chief-of-staff:daily
```

## What It Does

This command orchestrates multiple sub-agents in sequence:

1. **Status Check** - Quick overview of what needs attention
2. **Package Processing** - Add new tracking numbers to Parcel
3. **Interactive Triage** - Process inbox with questions-first flow
4. **Digest Generation** - Summarize remaining automated emails

## Workflow

```
┌────────────────────────────────────────────────┐
│           Chief-of-Staff Daily                 │
├────────────────────────────────────────────────┤
│                                                │
│  1. STATUS CHECK                               │
│     → Show inbox overview                      │
│     → Highlight urgent items                   │
│     → Show active deliveries                   │
│                                                │
│  2. PACKAGE PROCESSING (if any found)          │
│     → Scan for shipping emails                 │
│     → Add tracking to Parcel                   │
│     → Archive to Orders folder                 │
│                                                │
│  3. INTERACTIVE TRIAGE                         │
│     → Questions-first interview                │
│     → Collect all decisions                    │
│     → Execute in bulk                          │
│     → Learn from choices                       │
│                                                │
│  4. DIGEST (optional)                          │
│     → Summarize remaining automated emails     │
│     → Offer bulk actions                       │
│                                                │
└────────────────────────────────────────────────┘
```

## Example Session

```
Good morning! Let's get your inbox organized.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1: Status Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your inbox has 23 unread emails:
- 3 action items (Top of Mind)
- 2 shipping notifications
- 8 newsletters
- 10 archive-ready

Active deliveries:
- FedEx: Arriving today (B&H Photo)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2: Package Processing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Found 2 shipping emails...
→ Added 1 new package to Parcel (REI - FedEx)
→ 1 Amazon email archived to Orders

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3: Interactive Triage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ready to process 21 remaining emails.
[Launches inbox-interviewer for Q&A session]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4: Daily Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
- 21 emails processed
- 12 archived, 5 deleted, 2 reminders, 2 kept
- 1 package added to Parcel
- Suggestion accuracy: 85%

Inbox is now clean!
```

## Implementation

This command orchestrates multiple agents sequentially:

```
1. Display status (inline, no sub-agent)
2. Task: chief-of-staff:inbox-to-parcel
3. Task: chief-of-staff:inbox-interviewer
4. Optional: Task: chief-of-staff:digest-generator
```

Each step waits for the previous to complete before proceeding.
