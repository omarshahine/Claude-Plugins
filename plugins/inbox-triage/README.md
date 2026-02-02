# inbox-triage

Self-learning email triage with questions-first interview flow, decision learning, visual HTML batch interface, and pattern recognition.

## Features

- **Questions-First Interview**: Fast Q&A - all questions up front, bulk execution at end
- **Decision Learning**: Records what you chose vs suggestions, improves over time
- **Visual Batch Triage**: HTML interface for reviewing all inbox emails at once
- **Pattern Learning**: Discovers filing patterns from existing folder organization
- **Smart Classification**: Categorizes emails (packages, newsletters, financial, action items)
- **Batch Orchestration**: Delegates to specialized sub-agents (parcel, newsletter, reminder)
- **Automated Digest**: Summarizes automated emails with priority categorization

## Commands

| Command | Description |
|---------|-------------|
| `/inbox-triage:setup` | Configure email provider |
| `/inbox-triage:learn` | Bootstrap rules from existing folders |
| `/inbox-triage:batch` | Visual HTML batch triage interface |
| `/inbox-triage:batch --process` | Process submitted batch decisions |
| `/inbox-triage:interview` | Voice-friendly one-by-one triage |
| `/inbox-triage:triage` | Process inbox with confirmation |
| `/inbox-triage:digest` | Summarize automated emails |
| `/inbox-triage:analyze` | Find Trash/Archive patterns |
| `/inbox-triage:suggest` | Recommend folder improvements |
| `/inbox-triage:optimize` | Deep scan folders for reorganization |
| `/inbox-triage:rules` | View/manage filing rules |

## Quick Start

```bash
# 1. Configure email provider
/inbox-triage:setup

# 2. Learn patterns from existing folders
/inbox-triage:learn

# 3. Choose your triage mode:

# Option A: Visual HTML batch (desktop, quick review)
/inbox-triage:batch
# Review in browser, click Submit All, then:
/inbox-triage:batch --process

# Option B: Voice interview (mobile, thorough)
/inbox-triage:interview
```

## Triage Modes

### Batch Mode (Visual HTML)

Best for desktop users who want to quickly review all emails at once.

1. Run `/inbox-triage:batch` to generate HTML interface
2. Browser opens with emails grouped by category
3. Review suggested actions, modify as needed
4. Click "Submit All" to download decisions
5. Run `/inbox-triage:batch --process` to execute

**Email Categories:**
- Top of Mind - Action items needing response
- Deliveries - Package shipments
- Newsletters - Marketing emails
- Financial - Banking alerts
- Archive Ready - High-confidence filing matches
- Delete Candidates - Likely deletable
- FYI - Everything else

### Interview Mode (Questions-First)

Fast voice-friendly mode with three phases:

```
PHASE 1: COLLECT (rapid Q&A)
→ Answer questions for each email
→ No waiting between emails

PHASE 2: EXECUTE (bulk processing)
→ All actions run at once
→ Single API call per folder

PHASE 3: LEARN (improve suggestions)
→ Record decisions vs suggestions
→ Update confidence scores
```

1. Run `/inbox-triage:interview`
2. Answer questions for each thread (fast - no execution between)
3. Confirm execution when all collected
4. System learns from your choices

**Voice Commands:**
- "archive", "delete", "reminder", "keep"
- "parcel" (for packages), "unsubscribe" (for newsletters)
- "stop" or "done" to end collection and execute

## How It Works

### Bootstrap Learning

1. Analyzes your existing folder organization
2. Samples emails from each folder
3. Extracts sender domain patterns
4. Calculates confidence based on exclusivity
5. Presents rules for your confirmation

### Confidence Scoring

| Confidence | Meaning |
|------------|---------|
| 90%+ | High reliability - consistent folder match |
| 70-89% | Good match - some variation |
| <70% | Not suggested - unreliable |

### Decision Learning

After each interview session, the system learns from your choices:

```
Suggestion accuracy: 12/15 (80%)

Confidence updates:
  ↑ chase.com → Financial (+5%)
  ↓ newsletters.example.com (-15%)

New pattern detected:
  → bestbuy.com → Orders (add rule? y/n)
```

| User Action | Effect |
|-------------|--------|
| Accept suggestion | +5% confidence (max 99%) |
| Reject suggestion | -15% confidence (min 10%) |
| Same domain → folder 3+ times | New rule proposed |
| Rule < 50% acceptance | Flagged for review |

### Folder Optimization

The `/inbox-triage:optimize` command performs deep analysis:

1. **Subfolder suggestions**: Identifies folders that could benefit from subdivision
   - Example: "Travel" with 800+ emails → suggest Flights, Hotels, Car Service subfolders
2. **Rule consistency**: Finds stale rules that no longer match folder contents
3. **Missing rules**: Identifies consistent patterns without corresponding rules
4. **Consolidation**: Suggests merging low-volume or overlapping folders
5. **Server-side candidates**: Patterns that could be automated at the mail server level

All changes require explicit confirmation before execution.

## Provider Support

- **Fastmail** (active)
- Gmail (future)
- Outlook (future)

## Requirements

- Email MCP server configured
- Existing folder structure to learn from

## License

MIT
