# Chief-of-Staff

The "one plugin to rule them all" for personal productivity. Chief-of-Staff is an uber-orchestrator that consolidates email triage, package tracking, reminder creation, and newsletter management into a single unified system.

## Installation

```bash
/plugin install chief-of-staff@omarshahine-agent-plugins
```

## Quick Start

```bash
# 1. Configure your email provider
/chief-of-staff:setup

# 2. Learn patterns from existing folders (optional but recommended)
/chief-of-staff:learn

# 3. Start triaging your inbox
/chief-of-staff:triage
```

## Commands

| Command | Description |
|---------|-------------|
| `/chief-of-staff:setup` | Configure email provider (Fastmail active) |
| `/chief-of-staff:daily` | Full daily orchestration routine |
| `/chief-of-staff:status` | Quick dashboard of inbox status |
| `/chief-of-staff:triage` | Interactive questions-first triage |
| `/chief-of-staff:batch` | Visual HTML batch interface |
| `/chief-of-staff:parcel` | Process shipping emails to Parcel app |
| `/chief-of-staff:reminders` | Create reminders from action items |
| `/chief-of-staff:unsubscribe` | Unsubscribe from newsletters |
| `/chief-of-staff:digest` | Summarize automated emails |
| `/chief-of-staff:learn` | Bootstrap or update filing rules |
| `/chief-of-staff:analyze` | Find patterns in Trash/Archive |
| `/chief-of-staff:optimize` | Deep folder analysis and suggestions |
| `/chief-of-staff:rules` | View/manage filing rules |

## Architecture

Chief-of-Staff contains 12 specialized sub-agents:

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

## Core Workflow

The core workflow is **questions-first**:

```
COLLECT -> EXECUTE -> LEARN
```

1. **COLLECT**: Ask questions for each email, store decisions (no API calls yet)
2. **EXECUTE**: Run all actions in bulk (efficient API usage)
3. **LEARN**: Record decisions, update confidence scores, detect patterns

## Data Files

All data is stored in `data/` (gitignored, with `.example.yaml` templates):

| File | Purpose |
|------|---------|
| `settings.yaml` | Provider configuration (email, parcel, reminders) |
| `user-preferences.yaml` | Sender overrides, never-file lists |
| `filing-rules.yaml` | Learned filing patterns with confidence |
| `delete-patterns.yaml` | Patterns for delete suggestions |
| `decision-history.yaml` | Learning data from triage sessions |
| `interview-state.yaml` | Resume state for triage sessions |
| `batch-state.yaml` | HTML batch triage session state |
| `newsletter-lists.yaml` | Allowlist and unsubscribed senders |

## Dependencies

**Required:**
- Email MCP server (Fastmail active; Gmail/Outlook planned)

**Optional (enhance functionality):**
- Parcel API MCP - Package tracking
- Apple PIM MCP - Reminders (`/plugin install apple-pim@omarshahine-agent-plugins`)
- Playwright plugin - Newsletter unsubscribe web forms

## Migration from Old Plugins

If migrating from standalone inbox-triage, inbox-to-parcel, etc., run:

```bash
./scripts/migrate-data.sh
```

See the main README for detailed migration instructions.

## Private Extensions

Power users can extend Chief-of-Staff with private capabilities by creating a separate private plugin that:

1. Adds custom agents for proprietary workflows
2. Includes a skill that teaches COS about the private agents
3. Private agents can call COS sub-agents via Task tool

Example skill in a private plugin:

```markdown
# skills/private-capabilities/SKILL.md
---
description: |
  Private agents available to Chief-of-Staff:
  - filing-cabinet-organizer: Manage Filing Cabinet documents
  - netjets-invoice-downloader: Download NetJets invoices
---

# Private Chief-of-Staff Capabilities
...
```

## License

MIT
