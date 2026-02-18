# Agent-Plugins

A personal plugin marketplace for Claude Code containing reusable plugins for email management, travel, personal information management, and productivity.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add omarshahine/agent-plugins
```

Install the main orchestrator plugin:

```bash
# Chief-of-Staff - the uber orchestrator for personal productivity
/plugin install chief-of-staff@omarshahine-agent-plugins

# Related plugins (optional, enhance COS capabilities)
/plugin install apple-pim@omarshahine-agent-plugins         # Calendar, Reminders, Contacts, Mail
/plugin install travel-agent@omarshahine-agent-plugins      # Flight research & tracking
/plugin install credit-card-benefits@omarshahine-agent-plugins  # Credit card benefit tracking
/plugin install rename-agent@omarshahine-agent-plugins      # AI-powered file renaming
```

---

## How It Works: The Plugin Ecosystem

**Chief-of-Staff** is the central orchestrator - "one plugin to rule them all" for personal productivity. It consolidates email triage, package tracking, reminder creation, and newsletter management into a single unified system.

```
+-----------------------------------------------------------------------+
|                        CHIEF-OF-STAFF                                 |
|                  "One Plugin to Rule Them All"                        |
|                                                                       |
|   Built-in Sub-Agents:              Related Plugins:                  |
|   - inbox-interviewer               - apple-pim (Calendar/Reminders/  |
|   - inbox-to-parcel                       Contacts/Mail)              |
|   - inbox-to-reminder               - travel-agent (Flights/Trips)    |
|   - newsletter-unsubscriber         - credit-card-benefits            |
|   - digest-generator                - rename-agent                    |
|   - organization-analyzer                                             |
|   - pattern-learner                                                   |
|   - folder-optimizer                                                  |
+-----------------------------------------------------------------------+
```

**When you run `/chief-of-staff:triage`, the orchestrator:**
1. Fetches emails from your inbox
2. Classifies each one (package, newsletter, financial, action item, etc.)
3. Suggests actions based on learned patterns
4. Routes to specialized sub-agents when you choose:
   - "Add to Parcel" -> `inbox-to-parcel` extracts tracking, adds to Parcel app
   - "Unsubscribe" -> `newsletter-unsubscriber` handles the unsubscribe flow
   - "Create reminder" -> `inbox-to-reminder` creates Apple Reminder via `apple-pim`

**Standalone plugins** (travel-agent, credit-card-benefits, rename-agent, apple-pim) work independently for their specific domains but integrate seamlessly with Chief-of-Staff.

---

## chief-of-staff

**The email orchestrator.** Self-learning email triage that classifies your inbox, suggests actions based on your patterns, and delegates to specialized sub-agents.

### Why Chief-of-Staff?

- **Questions-first flow**: Collect ALL decisions up front, execute in bulk at the end (faster)
- **Learns your patterns**: Records your choices vs suggestions, improves accuracy over time
- **Routes intelligently**: Detects packages, newsletters, and action items - sends them to the right handler
- **Multiple modes**: Interview mode (voice-friendly), batch mode (visual HTML), digest mode (summaries)
- **Unified interface**: One plugin, many capabilities

### Quick Start

```bash
# 1. Configure your email provider
/chief-of-staff:setup

# 2. Learn patterns from existing folders
/chief-of-staff:learn

# 3. Triage your inbox
/chief-of-staff:triage     # Interactive Q&A mode
# OR
/chief-of-staff:batch      # Visual HTML batch mode
```

### Commands

| Command | Description |
|---------|-------------|
| `/chief-of-staff:setup` | Configure email provider (Fastmail, Gmail, Outlook) |
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

### Triage Modes

| Mode | Best For | How It Works |
|------|----------|--------------|
| `/chief-of-staff:triage` | Mobile, voice, thorough review | One-by-one Q&A with structured options |
| `/chief-of-staff:batch` | Desktop, quick visual review | HTML interface, review all at once |
| `/chief-of-staff:digest` | Quick status | Summary of automated emails |

### Interview Mode Flow

```
PHASE 1: COLLECT (rapid Q&A)
-> Answer questions for each email
-> No waiting between emails

PHASE 2: EXECUTE (bulk processing)
-> All actions run at once
-> Single API call per folder

PHASE 3: LEARN (improve suggestions)
-> Record decisions vs suggestions
-> Update confidence scores
```

### Custom Responses During Interview

| You Say | What Happens |
|---------|--------------|
| "Need to create a rule" | Archives + creates reminder to make a server-side rule |
| "Flag for later" | Keeps in inbox + flags for follow-up |
| "Read and summarize" | Summarizes content, shows at end, then archives/deletes |

### Built-in Sub-Agents

Chief-of-Staff includes these specialized agents that handle specific email types:

#### inbox-to-parcel

Extracts tracking numbers from shipping emails and adds to Parcel app.

- Supports: UPS, FedEx, USPS, DHL, OnTrac, Amazon
- Moves processed emails to Orders folder
- **Direct command**: `/chief-of-staff:parcel`
- **Requires**: Parcel, Playwright MCPs (email loads via ToolSearch)

#### newsletter-unsubscriber

Handles unwanted newsletter unsubscription.

- Detects newsletters via RFC 2369 headers (List-Unsubscribe)
- Executes via mailto or web forms (uses Playwright)
- Maintains allowlist of wanted newsletters
- **Direct command**: `/chief-of-staff:unsubscribe`
- **Requires**: Playwright MCP (email loads via ToolSearch)

#### inbox-to-reminder

Creates Apple Reminders from emails requiring action.

- Identifies bills, deadlines, follow-ups, meeting requests
- Creates reminders with appropriate due dates
- Routes to correct reminder list
- **Direct command**: `/chief-of-staff:reminders`
- **Requires**: `apple-pim` plugin (loads via ToolSearch)

#### Other Sub-Agents

| Agent | Purpose |
|-------|---------|
| `inbox-interviewer` | Interactive questions-first triage |
| `digest-generator` | Summarize automated emails |
| `organization-analyzer` | Analyze Trash/Archive patterns |
| `pattern-learner` | Bootstrap filing rules from folders |
| `folder-optimizer` | Suggest folder reorganization |
| `decision-learner` | Learn from triage decisions |
| `batch-html-generator` | Visual batch triage interface |
| `batch-processor` | Execute batch triage decisions |

### Requirements

- Email MCP server (Fastmail, Gmail, or Outlook) - see setup below
- Existing folder structure to learn from

### Email MCP Setup (Required)

**Chief-of-Staff does NOT bundle an email MCP server.** You must configure your email provider separately.

#### Fastmail (Recommended)

Deploy your own Fastmail MCP server using Cloudflare Workers:

**Repository:** [omarshahine/fastmail-mcp-remote](https://github.com/omarshahine/fastmail-mcp-remote)

```bash
# After deploying, add to Claude Code:
claude mcp add --transport http fastmail https://your-worker.workers.dev/mcp
```

#### Gmail

**Official Integration:** Google services are available as [official integrations in Claude](https://www.anthropic.com/integrations). Enable Google Drive, Docs, and Gmail directly in Claude's settings.

**MCP Server:** For Claude Code CLI usage, use the Smithery Gmail server:
- [smithery.ai/server/gmail](https://smithery.ai/server/gmail)

#### Outlook / Microsoft 365

**Official Integration:** Microsoft services are available as [official integrations in Claude](https://www.anthropic.com/integrations). Enable Outlook, OneDrive, and other M365 services directly in Claude's settings.

**MCP Server:** For Claude Code CLI usage, use the Smithery Outlook server:
- [smithery.ai/server/outlook](https://smithery.ai/server/outlook)

#### Verification

After adding your email MCP, verify it's working:

```bash
# Check MCP status
/mcp

# Run setup to configure Chief-of-Staff
/chief-of-staff:setup
```

### Provider-Agnostic Architecture

Chief-of-Staff agents are **email provider-agnostic**. The active email provider is configured in `settings.yaml`, and agents dynamically load the appropriate email tools via ToolSearch at runtime.

Only **fixed** integrations (Parcel, Playwright, Apple PIM) are declared in agent frontmatter. This means:
- Switch email providers by updating `settings.yaml` - no agent changes needed
- Gmail and Outlook support ready when MCP servers are available

### Private Extensions

Power users can extend Chief-of-Staff with private capabilities by creating a separate private plugin (e.g., `chief-of-staff-private`) that:

1. Adds custom agents for proprietary workflows
2. Includes a skill that teaches COS about the private agents
3. Private agents can call COS sub-agents via Task tool

See CLAUDE.md for the private extension pattern.

---

## travel-agent

Flight research and trip tracking using multiple data sources.

### Agents

| Agent | Model | Description |
|-------|-------|-------------|
| `google-flights` | sonnet | Search Google Flights for airfare pricing |
| `ita-matrix` | sonnet | Advanced fare research with detailed pricing rules |
| `flighty` | haiku | Query Flighty app for flight tracking |
| `tripsy` | haiku | Query Tripsy app for trip planning |

### google-flights

Search Google Flights for airfare estimates.

**Best for:** Quick price comparisons, date flexibility research, routing options

**Example:**
```
Search business class flights from Seattle to Hong Kong for December 2026
```

**Requires:** `pip install fast-flights`

### ita-matrix

Search ITA Matrix for detailed fare information.

**Best for:** Fare class research, pricing breakdowns, complex routing rules

**Note:** Uses headed browser (ITA blocks headless). Searches take 2-5 minutes.

**Requires:** `/plugin install playwright@claude-plugins-official`

### flighty

Query Flighty app's local database for flight tracking.

**Commands:**
| Command | Description |
|---------|-------------|
| `list [limit]` | Upcoming flights |
| `next` | Next upcoming flight |
| `date YYYY-MM-DD` | Flights on a date |
| `pnr CODE` | Search by confirmation code |
| `stats` | Flight statistics |
| `recent [limit]` | Past flights |

**Requires:** Flighty app on macOS

### tripsy

Query Tripsy app's local database for trip information.

**Commands:**
| Command | Description |
|---------|-------------|
| `list [limit]` | Upcoming trips |
| `trip "Name"` | Full trip details |
| `flights [limit]` | Flights across all trips |
| `hotels [limit]` | Hotel stays |

**Requires:** Tripsy app on macOS

---

## apple-pim

Native macOS integration for Calendar, Reminders, Contacts, and Mail using Apple's EventKit, Contacts, and JXA frameworks. Built with Swift CLIs wrapped by a Node.js MCP server.

**Source:** [omarshahine/Apple-PIM-Agent-Plugin](https://github.com/omarshahine/Apple-PIM-Agent-Plugin)

> This plugin is sourced from an external GitHub repo - see the link above for full documentation, architecture details, and development instructions.

### Features

- Full CRUD for events, reminders, contacts, and mail messages
- 32 MCP tools across 4 domains (Calendar, Reminders, Contacts, Mail)
- Batch operations for creating multiple events or reminders at once
- Natural language dates ("tomorrow 2pm", "next Tuesday", "in 2 hours")
- Recurrence rules (daily, weekly, monthly, yearly with patterns)
- Configurable per-domain enable/disable and calendar/list filtering
- Used by `chief-of-staff:reminders` for creating reminders from emails

### Installation

```bash
/plugin install apple-pim@omarshahine-agent-plugins

# Build Swift CLIs and install dependencies
~/.claude/plugins/cache/omarshahine-agent-plugins/apple-pim/setup.sh
```

Restart Claude Code to load the MCP server, then grant macOS permissions when prompted (Calendar, Reminders, Contacts). For mail, also grant Automation permission for Mail.app.

### Usage

**Slash commands:**
```
/apple-pim:calendars events
/apple-pim:calendars create "Team Meeting" --start "tomorrow 2pm" --duration 60
/apple-pim:reminders items --list "Shopping"
/apple-pim:reminders create "Buy milk" --due "tomorrow"
/apple-pim:contacts search "John"
/apple-pim:mail messages --mailbox "INBOX" --filter unread
```

**Natural language (via pim-assistant agent):**
```
Schedule a meeting with the team for next Tuesday at 2pm
Remind me to call the dentist tomorrow
What's on my calendar this week?
Find John's phone number
Show me unread emails in my inbox
```

### Commands

| Command | Description |
|---------|-------------|
| `/apple-pim:calendars` | Manage calendar events (list, search, create, update, delete) |
| `/apple-pim:reminders` | Manage reminders (list, search, create, complete, update, delete) |
| `/apple-pim:contacts` | Manage contacts (list, search, get details, create, update, delete) |
| `/apple-pim:mail` | Manage Mail.app messages (list, search, read, flag, move, delete) |
| `/apple-pim:configure` | Interactive setup - enable/disable domains, filter calendars/lists |

### Requirements

- macOS 13+ (Ventura or later)
- Swift 5.9+ (Xcode 15+ or Command Line Tools)
- Node.js 18+
- Mail.app must be running for mail commands
- Grant Calendar, Reminders, Contacts, and Automation permissions when prompted

---

## credit-card-benefits

Track and maximize premium credit card benefits with anniversary-aware checklists.

### Supported Cards

| Card | Annual Fee | Key Benefits |
|------|------------|--------------|
| Amex Platinum | $895 | Monthly Uber/streaming, quarterly dining, annual airline |
| Venture X | $395 | Annual travel credit, anniversary miles |
| Chase Sapphire Reserve | $795 | Travel credit, DoorDash, Instacart |
| Delta SkyMiles Reserve | $650 | Companion cert, Delta Stays, monthly credits |
| Alaska Airlines Atmos Summit | $395 | Companion fare, lounge passes |

### Quick Start

```bash
/plugin install credit-card-benefits@omarshahine-agent-plugins

/credit-card-benefits:configure    # Set up cards and data source
/credit-card-benefits:sync --full  # Pull 12 months to find anniversaries
/credit-card-benefits:status       # Check your benefits
```

### Commands

| Command | Description |
|---------|-------------|
| `/credit-card-benefits:configure` | Set up cards and data sources |
| `/credit-card-benefits:sync` | Sync transactions |
| `/credit-card-benefits:status` | View all benefits |
| `/credit-card-benefits:remind` | Benefits expiring soon |
| `/credit-card-benefits:use` | Record benefit usage |
| `/credit-card-benefits:info` | Card benefit details |

### Data Sources

| Source | Best For |
|--------|----------|
| YNAB MCP | YNAB users with MCP server |
| YNAB API | YNAB users (requires token) |
| CSV Import | Any card |
| Manual | Simple tracking |

### Natural Language

```
What Amex credits do I still need to use?
Show me my unused Chase Sapphire benefits
What benefits are expiring this month?
```

---

## rename-agent

AI-powered file renaming with pattern-based naming.

### Features

- Analyzes PDFs, images, and text files
- Smart classification (15+ document types)
- Pattern learning for consistent naming
- Batch processing

### Usage

```
/rename-agent:rename ~/Downloads/tax-docs
/rename-agent:rename ~/Documents/receipts --pattern "{Date:YYYY-MM-DD} - {Merchant}"
```

Or natural language:
```
Rename the tax documents in my Downloads folder
Help me organize these receipts
```

### Pattern Tokens

`{Date:YYYY-MM-DD}`, `{Year}`, `{Merchant}`, `{Amount}`, `{Institution}`, `{Form Type}`, `{Last 4 Digits}`, `{Description}`

### Document Types

Receipt, Bill, Tax Document, Bank Statement, Invoice, Contract, Medical, Insurance, Investment, Payslip, Identity, Correspondence, Manual, Photo, General

### Requirements

- Python 3.10+
- `ANTHROPIC_API_KEY` environment variable
- Install: `pip install claude-rename-agent`

**Source:** https://github.com/omarshahine/claude-rename-agent

---

## Plugin Reference

| Plugin | Description | Key Commands |
|--------|-------------|--------------|
| **chief-of-staff** | Email orchestrator with learning | `/chief-of-staff:triage`, `/chief-of-staff:daily` |
| travel-agent | Flight research & tracking | Natural language queries |
| [apple-pim](https://github.com/omarshahine/Apple-PIM-Agent-Plugin) | Calendar, Reminders, Contacts, Mail | `/apple-pim:calendars`, `/apple-pim:reminders`, `/apple-pim:mail` |
| credit-card-benefits | Benefit tracking | `/credit-card-benefits:status` |
| rename-agent | File renaming | `/rename-agent:rename` |

---

## Creating New Plugins

1. Create directory: `plugins/my-plugin/`
2. Add manifest: `plugins/my-plugin/.claude-plugin/plugin.json`
3. Add agents, skills, or commands
4. Register in `.claude-plugin/marketplace.json`
5. Update this README

### Plugin Structure

```
plugins/
└── my-plugin/
    ├── .claude-plugin/
    │   └── plugin.json
    ├── agents/
    │   └── my-agent.md
    ├── skills/
    │   └── my-skill/
    │       └── SKILL.md
    ├── commands/
    │   └── my-command.md
    └── README.md
```

### Marketplace Configuration

Add to `.claude-plugin/marketplace.json`:

```json
{
  "name": "my-plugin",
  "source": "./plugins/my-plugin",
  "description": "Description of my plugin",
  "version": "1.0.0",
  "keywords": ["keyword1", "keyword2"],
  "category": "productivity"
}
```

---

## Migrating from Previous Plugins

If you were using the standalone inbox plugins (inbox-triage, inbox-to-parcel, inbox-to-reminder, newsletter-unsubscriber), follow these steps to migrate to Chief-of-Staff.

### Step 1: Backup Existing Data

```bash
# Find your old plugin data directories
ls ~/.claude/plugins/cache/omarshahine-agent-plugins/inbox-triage/data/
ls ~/.claude/plugins/cache/omarshahine-agent-plugins/inbox-to-parcel/data/
ls ~/.claude/plugins/cache/omarshahine-agent-plugins/inbox-to-reminder/data/
ls ~/.claude/plugins/cache/omarshahine-agent-plugins/newsletter-unsubscriber/data/

# Backup important files (filing rules, settings, learned patterns)
cp ~/.claude/plugins/cache/omarshahine-agent-plugins/inbox-triage/data/*.yaml ~/Desktop/inbox-backup/
```

### Step 2: Uninstall Old Plugins

```bash
/plugin uninstall inbox-triage@omarshahine-agent-plugins
/plugin uninstall inbox-to-parcel@omarshahine-agent-plugins
/plugin uninstall inbox-to-reminder@omarshahine-agent-plugins
/plugin uninstall newsletter-unsubscriber@omarshahine-agent-plugins
```

### Step 3: Install Chief-of-Staff

```bash
/plugin install chief-of-staff@omarshahine-agent-plugins
```

### Step 4: Migrate Data

Run the included migration script:

```bash
~/.claude/plugins/cache/omarshahine-agent-plugins/chief-of-staff/scripts/migrate-data.sh
```

Or manually copy your data files:

```bash
# Copy filing rules (most important - your learned patterns)
cp ~/Desktop/inbox-backup/filing-rules.yaml \
   ~/.claude/plugins/cache/omarshahine-agent-plugins/chief-of-staff/data/

# Copy user preferences
cp ~/Desktop/inbox-backup/user-preferences.yaml \
   ~/.claude/plugins/cache/omarshahine-agent-plugins/chief-of-staff/data/

# Copy settings (review and merge if needed)
cp ~/Desktop/inbox-backup/settings.yaml \
   ~/.claude/plugins/cache/omarshahine-agent-plugins/chief-of-staff/data/
```

### Step 5: Update Your Workflow

| Old Command | New Command |
|-------------|-------------|
| `/inbox-triage:interview` | `/chief-of-staff:triage` |
| `/inbox-triage:batch` | `/chief-of-staff:batch` |
| `/inbox-triage:learn` | `/chief-of-staff:learn` |
| `/inbox-triage:digest` | `/chief-of-staff:digest` |
| `/inbox-triage:rules` | `/chief-of-staff:rules` |
| `/inbox-triage:analyze` | `/chief-of-staff:analyze` |
| `/inbox-triage:optimize` | `/chief-of-staff:optimize` |
| `/inbox-to-parcel:track` | `/chief-of-staff:parcel` |
| `/inbox-to-reminder:scan` | `/chief-of-staff:reminders` |
| `/newsletter-unsubscriber:unsubscribe` | `/chief-of-staff:unsubscribe` |

### Data File Mapping

| Old Location | New Location |
|--------------|--------------|
| `inbox-triage/data/filing-rules.yaml` | `chief-of-staff/data/filing-rules.yaml` |
| `inbox-triage/data/user-preferences.yaml` | `chief-of-staff/data/user-preferences.yaml` |
| `inbox-triage/data/settings.yaml` | `chief-of-staff/data/settings.yaml` |
| `inbox-triage/data/delete-patterns.yaml` | `chief-of-staff/data/delete-patterns.yaml` |
| `inbox-to-parcel/data/settings.yaml` | Merged into `chief-of-staff/data/settings.yaml` |
| `newsletter-unsubscriber/data/newsletter-lists.yaml` | `chief-of-staff/data/newsletter-lists.yaml` |

---

## License

MIT
