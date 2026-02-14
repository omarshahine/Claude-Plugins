---
name: chief-of-staff
description: |
  Chief-of-Staff is the orchestrator plugin for personal productivity. Use this knowledge when:
  - User asks about inbox management, email triage, or filing
  - User mentions packages, shipping, or Parcel app
  - User wants to create reminders from emails
  - User mentions newsletters or unsubscribing
  - User asks about their daily routine or productivity workflow
  - User asks about iMessages, text messages, or SMS
  - User wants to read, search, or send a text/iMessage
  - User summons their persona by name (e.g., "Friday", "Max", "Jarvis")
---

# Chief-of-Staff Knowledge

Chief-of-Staff is an uber-orchestrator plugin that consolidates multiple email and productivity capabilities into one unified system.

## Persona System

Configurable persona with custom identity and dynamic summon command (e.g., `/friday`, `/jarvis`). Set up via `/chief-of-staff:setup`. See [references/persona-system.md](references/persona-system.md) for configuration details, greeting styles, and sub-commands.

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
| `imessage-assistant` | Read and send iMessages via CLI |

## Email Action Routes

Action routes extend the triage system to route emails to specialized agents for active processing. While filing rules route emails to folders, action routes route emails to agents.

### How It Works

```
Email arrives in inbox
    ↓
Triage (batch or interactive)
    ↓
Route matcher checks email-action-routes.yaml
    ↓
Match found? → Suggest "Process: [label]" as action
    ↓ (user confirms)
Invoke agent via Task tool
    ↓
Post-action (archive/delete/keep)
```

### Route Matching

Routes are checked in priority order (same as filing rules):
1. `sender_email` — Exact sender email match (highest priority)
2. `sender_domain` — Domain-level match
3. `subject_pattern` — Subject line regex match
4. `combined` — Domain + subject combination

Each route specifies:
- **Match criteria**: email/domain/pattern + optional refinements (subject_pattern, attachment_required)
- **Target**: `route.plugin` + `route.agent` (resolves to Task subagent_type)
- **Label**: Human-readable name shown in triage ("Process LF Invoice")
- **Post-action**: What to do with email after processing (archive/delete/keep/none)

### Integration Points

- **Batch HTML Generator**: Emails matching routes appear in the "Actionable" category (priority 0, before all other categories)
- **Batch Processor**: Route decisions invoke the target agent via Task tool, then execute the post-action
- **Inbox Interviewer**: Route matches surface as "Process: [label]" in the interactive interview options
- **Decision Learner**: Route decisions update confidence scores and detect new route-worthy patterns

### Route Configuration

Routes are configured in `email-action-routes.yaml` (mirrors `filing-rules.yaml` structure):

```yaml
routes:
  sender_email:
    - email: "accounting@vendor.example.com"
      attachment_required: true
      route:
        plugin: "my-plugin"
        agent: "invoice-processor"
        label: "Process Vendor Invoice"
        pass_attachments: true
        post_action: "archive"
        post_action_folder: "Invoices"
      confidence: 0.95
      source: "manual"
      enabled: true
```

### Managing Routes

Use `/chief-of-staff:routes` to list, add, remove, and toggle routes.

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
| `/chief-of-staff:routes` | View/manage email action routes |
| `/chief-of-staff:imessage` | Read, search, and send iMessages |

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
| `email-action-routes.yaml` | Action routes mapping emails to skills/agents |

## Pattern Files

Pattern files for email classification in `assets/`:

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

- **Email MCP** - Email provider (required, user-configured separately)
- **Parcel API MCP** - Package tracking (bundled)
- **Playwright MCP** - Newsletter unsubscribe web forms (bundled)
- **Apple PIM MCP** - Reminders and calendar (optional, separate plugin)
- **imsg CLI** - iMessage access (required for imessage-assistant, `brew install steipete/tap/imsg`)

## Email Provider Setup (Required)

Chief-of-Staff does NOT bundle an email MCP server. Run `/chief-of-staff:setup` to configure. Supports Fastmail, Gmail, and Outlook. See [references/email-provider-setup.md](references/email-provider-setup.md) for setup instructions, Cowork configuration, and troubleshooting.

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
