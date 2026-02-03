---
description: |
  Chief-of-Staff is the orchestrator plugin for personal productivity. Use this knowledge when:
  - User asks about inbox management, email triage, or filing
  - User mentions packages, shipping, or Parcel app
  - User wants to create reminders from emails
  - User mentions newsletters or unsubscribing
  - User asks about their daily routine or productivity workflow
  - User summons their persona by name (e.g., "Friday", "Max", "Jarvis")
---

# Chief-of-Staff Knowledge

Chief-of-Staff is an uber-orchestrator plugin that consolidates multiple email and productivity capabilities into one unified system.

## Persona System

Chief-of-Staff supports a configurable **persona** that gives the assistant a custom identity and dynamic summon command.

### Configuration

Persona settings are stored in `data/settings.yaml`:

```yaml
persona:
  name: Friday            # Assistant's name
  user_name: Jane         # User's name (optional)
  greeting_style: friendly # professional, friendly, casual
```

### Dynamic Summon Command

When configured, a personalized command is created at `~/.claude/commands/<name>.md`:
- Persona "Friday" → `/friday`
- Persona "Max" → `/max`
- Persona "Jarvis" → `/jarvis`

### Summon Command Features

The summon command (`/friday`, etc.) provides:

1. **Quick Assessment**: Inbox status, active deliveries, due reminders
2. **Contextual Suggestions**: Recommends actions based on current state
3. **Sub-command Routing**: `/friday triage`, `/friday parcel`, etc.

### Greeting Styles

| Style | Example |
|-------|---------|
| professional | "Good morning. Here's your current status." |
| friendly | "Good morning! Let's see what we've got today." |
| casual | "Hey! Here's what's happening." |

### Sub-commands

| Command | Routes To |
|---------|-----------|
| `/friday` | Quick assessment + suggestions |
| `/friday triage` | `/chief-of-staff:triage` |
| `/friday parcel` | `/chief-of-staff:parcel` |
| `/friday status` | `/chief-of-staff:status` |
| `/friday daily` | `/chief-of-staff:daily` |
| `/friday reminders` | `/chief-of-staff:reminders` |

## Architecture

Chief-of-Staff contains these sub-agents:

| Agent | Purpose |
|-------|---------|
| `inbox-interviewer` | Interactive questions-first inbox triage |
| `inbox-to-parcel` | Package tracking from shipping emails |
| `inbox-to-reminder` | Create reminders from action items |
| `newsletter-unsubscriber` | Unsubscribe from unwanted newsletters |
| `digest-generator` | Summarize automated emails |
| `organization-analyzer` | Analyze Trash/Archive patterns |
| `pattern-learner` | Bootstrap filing rules from folders |
| `inbox-triage` | Apply learned rules to inbox |
| `folder-optimizer` | Suggest folder reorganization |
| `decision-learner` | Learn from triage decisions |
| `batch-html-generator` | Visual batch triage interface |
| `batch-processor` | Execute batch triage decisions |

## Commands

| Command | Description |
|---------|-------------|
| `/chief-of-staff:setup` | Configure email provider and integrations |
| `/chief-of-staff:daily` | Full daily orchestration routine |
| `/chief-of-staff:status` | Quick dashboard of inbox status |
| `/chief-of-staff:triage` | Interactive inbox interview |
| `/chief-of-staff:parcel` | Process shipping emails |
| `/chief-of-staff:reminders` | Create reminders from emails |
| `/chief-of-staff:unsubscribe` | Unsubscribe from newsletters |
| `/chief-of-staff:digest` | Summarize automated emails |
| `/chief-of-staff:learn` | Bootstrap or update filing rules |
| `/chief-of-staff:analyze` | Analyze Trash/Archive patterns |
| `/chief-of-staff:optimize` | Suggest folder reorganization |
| `/chief-of-staff:batch` | Visual HTML batch interface |
| `/chief-of-staff:rules` | View/manage filing rules |

## Data Files

All data is stored in the plugin's `data/` directory:

| File | Purpose |
|------|---------|
| `settings.yaml` | Provider configuration (email, parcel, reminders) |
| `user-preferences.yaml` | Sender overrides, never-file lists, digest prefs |
| `filing-rules.yaml` | Learned filing patterns with confidence |
| `delete-patterns.yaml` | Patterns for delete suggestions |
| `decision-history.yaml` | Learning data from triage sessions |
| `interview-state.yaml` | Resume state for triage sessions |
| `batch-state.yaml` | HTML batch triage session state |
| `newsletter-lists.yaml` | Allowlist and unsubscribed senders |

## Pattern Files

Pattern files for email classification in `templates/`:

| File | Purpose |
|------|---------|
| `shipping-patterns.json` | Carrier patterns, tracking regex, search queries |
| `newsletter-patterns.json` | RFC headers, bulk sender patterns, unsubscribe detection |
| `batch-triage.html` | HTML template for visual batch interface |

## Workflow: Questions-First Triage

The core workflow is **questions-first**:

```
COLLECT → EXECUTE → LEARN
```

1. **COLLECT**: Ask questions for each email, store decisions (no API calls)
2. **EXECUTE**: Run all actions in bulk (efficient API usage)
3. **LEARN**: Record decisions, update confidence scores, detect patterns

## Integration Dependencies

Chief-of-Staff integrates with:

- **Fastmail MCP** - Email provider (required)
- **Parcel API MCP** - Package tracking (optional)
- **Apple PIM MCP** - Reminders and calendar (optional)
- **Playwright MCP** - Newsletter unsubscribe web forms (optional)

## Private Extensions

Users can extend Chief-of-Staff with private capabilities by:

1. Creating a separate private plugin (e.g., `chief-of-staff-private`)
2. Adding a skill that teaches COS about the private agents
3. Private agents can call COS sub-agents via Task tool

Example private extension skill:
```markdown
# skills/private-capabilities/SKILL.md
---
description: |
  Private agents available to Chief-of-Staff:
  - filing-cabinet-organizer: Manage Filing Cabinet documents
  - netjets-invoice-downloader: Download NetJets invoices
---

# Private Chief-of-Staff Capabilities
[Documentation of private agents]
```

## Key Design Principles

1. **INBOX-ONLY**: Never process already-archived emails
2. **DEDUPLICATION**: Always check before adding (Parcel rate limits)
3. **USER CONFIRMATION**: Never auto-file without explicit approval
4. **LEARNING**: Record decisions to improve future suggestions
5. **BULK OPERATIONS**: Group API calls for efficiency
6. **VOICE-FRIENDLY**: Simple numbered options for voice input

## Output Formatting Guidelines

When displaying information to the user:

1. **NO EMOJIS IN TABLE CELLS**: Emojis have inconsistent display widths and break markdown table column alignment in terminal rendering. Use plain text in tables.

   **Bad:**
   ```
   | Folder | Unread |
   |--------|--------|
   | 📦 Orders | 222 |
   | 🛩️ Flights | 29 |
   ```

   **Good:**
   ```
   | Folder | Unread |
   |--------|--------|
   | Orders | 222 |
   | Flights | 29 |
   ```

2. **EMOJIS IN HEADERS ARE OK**: Section headers like `## 📬 Inbox Overview` render fine.

3. **EMOJIS IN LISTS ARE OK**: Bullet points with emojis work correctly.

4. **KEEP TABLES SIMPLE**: Avoid complex formatting, long text, or special characters in table cells.
