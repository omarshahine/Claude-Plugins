# Agent-Plugins

A personal plugin marketplace for Claude Code containing reusable plugins for email management, travel, personal information management, and productivity.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add omarshahine/agent-plugins
```

Install the plugins you need:

```bash
/plugin install inbox-triage@omarshahine-agent-plugins      # Email orchestrator
/plugin install travel-agent@omarshahine-agent-plugins      # Flight research & tracking
/plugin install apple-pim@omarshahine-agent-plugins         # Calendar, Reminders, Contacts
/plugin install credit-card-benefits@omarshahine-agent-plugins  # Credit card benefit tracking
/plugin install rename-agent@omarshahine-agent-plugins      # AI-powered file renaming
```

---

## How It Works: The Plugin Ecosystem

These plugins are designed to work together. At the center is **inbox-triage**, which acts as an orchestrator for email management, automatically delegating to specialized sub-plugins.

```
                    +------------------------+
                    |     inbox-triage       |
                    |  (Email Orchestrator)  |
                    +------------------------+
                              |
            +-----------------+-----------------+
            |                 |                 |
            v                 v                 v
    +---------------+ +---------------+ +---------------+
    | inbox-to-     | | newsletter-   | | inbox-to-     |
    | parcel        | | unsubscriber  | | reminder      |
    +---------------+ +---------------+ +---------------+
            |                 |                 |
            v                 v                 v
    +---------------+ +---------------+ +---------------+
    | Parcel App    | | Playwright    | | apple-pim     |
    +---------------+ +---------------+ +---------------+
```

**When you run `/inbox-triage:interview`, the orchestrator:**
1. Fetches emails from your inbox
2. Classifies each one (package, newsletter, financial, action item, etc.)
3. Suggests actions based on learned patterns
4. Routes to specialized handlers when you choose:
   - "Add to Parcel" → `inbox-to-parcel` extracts tracking, adds to Parcel app
   - "Unsubscribe" → `newsletter-unsubscriber` handles the unsubscribe flow
   - "Create reminder" → `inbox-to-reminder` creates Apple Reminder via `apple-pim`

**Standalone plugins** (travel-agent, credit-card-benefits, rename-agent) work independently for their specific domains.

---

## inbox-triage

**The email orchestrator.** Self-learning email triage that classifies your inbox, suggests actions based on your patterns, and delegates to specialized plugins.

### Why inbox-triage?

- **Questions-first flow**: Collect ALL decisions up front, execute in bulk at the end (faster)
- **Learns your patterns**: Records your choices vs suggestions, improves accuracy over time
- **Routes intelligently**: Detects packages, newsletters, and action items—sends them to the right handler
- **Multiple modes**: Interview mode (voice-friendly), batch mode (visual HTML), digest mode (summaries)

### Quick Start

```bash
# 1. Configure your email provider
/inbox-triage:setup

# 2. Learn patterns from existing folders
/inbox-triage:learn

# 3. Triage your inbox
/inbox-triage:interview     # Interactive Q&A mode
# OR
/inbox-triage:batch         # Visual HTML batch mode
```

### Triage Modes

| Mode | Best For | How It Works |
|------|----------|--------------|
| `/inbox-triage:interview` | Mobile, voice, thorough review | One-by-one Q&A with structured options |
| `/inbox-triage:batch` | Desktop, quick visual review | HTML interface, review all at once |
| `/inbox-triage:digest` | Quick status | Summary of automated emails |

### Commands

| Command | Description |
|---------|-------------|
| `/inbox-triage:setup` | Configure email provider (Fastmail active) |
| `/inbox-triage:learn` | Bootstrap rules from existing folders |
| `/inbox-triage:interview` | Interactive questions-first triage |
| `/inbox-triage:batch` | Visual HTML batch interface |
| `/inbox-triage:batch --process` | Execute batch decisions |
| `/inbox-triage:triage` | Process inbox with confirmation |
| `/inbox-triage:digest` | Summarize automated emails |
| `/inbox-triage:rules` | View/manage filing rules |
| `/inbox-triage:optimize` | Deep folder analysis and suggestions |
| `/inbox-triage:analyze` | Find patterns in Trash/Archive |

### Interview Mode Flow

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

### Custom Responses During Interview

| You Say | What Happens |
|---------|--------------|
| "Need to create a rule" | Archives + creates reminder to make Fastmail rule |
| "Flag for later" | Keeps in inbox + flags for follow-up |
| "Read and summarize" | Summarizes content, shows at end, then archives/deletes |

### Sub-Plugins (Automatic Delegation)

When inbox-triage detects specific email types, it routes to specialized handlers:

#### inbox-to-parcel

Extracts tracking numbers from shipping emails and adds to Parcel app.

- Supports: UPS, FedEx, USPS, DHL, OnTrac, Amazon
- Moves processed emails to Orders folder
- **Standalone**: `/inbox-to-parcel:track`
- **Requires**: Email MCP + Parcel API MCP server

#### newsletter-unsubscriber

Handles unwanted newsletter unsubscription.

- Detects newsletters via RFC 2369 headers (List-Unsubscribe)
- Executes via mailto or web forms (uses Playwright)
- Maintains allowlist of wanted newsletters
- **Standalone**: `/newsletter-unsubscriber:unsubscribe`
- **Requires**: Email MCP + Playwright plugin

#### inbox-to-reminder

Creates Apple Reminders from emails requiring action.

- Identifies bills, deadlines, follow-ups, meeting requests
- Creates reminders with appropriate due dates
- Routes to correct reminder list
- **Standalone**: `/inbox-to-reminder:scan`
- **Requires**: Email MCP + `apple-pim` plugin

### Requirements

- Email MCP server (Fastmail active; Gmail/Outlook planned)
- Existing folder structure to learn from

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

Native macOS integration for Calendar, Reminders, and Contacts.

### Features

- Full CRUD operations for events, reminders, and contacts
- Natural language dates ("tomorrow 2pm", "next Tuesday")
- MCP server for direct tool access
- Used by `inbox-to-reminder` for creating reminders from emails

### Installation

```bash
/plugin install apple-pim@omarshahine-agent-plugins

# Build Swift CLIs and install dependencies
~/.claude/plugins/cache/omarshahine-agent-plugins/apple-pim/setup.sh
```

Restart Claude Code to load the MCP server.

### Usage

**Slash commands:**
```
/apple-pim:calendars events
/apple-pim:calendars create "Team Meeting" --start "tomorrow 2pm" --duration 60
/apple-pim:reminders items --list "Shopping"
/apple-pim:reminders create "Buy milk" --due "tomorrow"
/apple-pim:contacts search "John"
```

**Natural language (via pim-assistant agent):**
```
Schedule a meeting with the team for next Tuesday at 2pm
Remind me to call the dentist tomorrow
What's on my calendar this week?
Find John's phone number
```

### Commands

| Command | Description |
|---------|-------------|
| `/apple-pim:calendars` | Manage calendar events |
| `/apple-pim:reminders` | Manage reminders |
| `/apple-pim:contacts` | Manage contacts |

### Requirements

- macOS 14+ (Sonoma) recommended
- Xcode Command Line Tools
- Node.js 18+
- Grant Calendar, Reminders, and Contacts access when prompted

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
| **inbox-triage** | Email orchestrator with learning | `/inbox-triage:interview`, `/inbox-triage:batch` |
| inbox-to-parcel | Package tracking from emails | `/inbox-to-parcel:track` |
| newsletter-unsubscriber | Newsletter management | `/newsletter-unsubscriber:unsubscribe` |
| inbox-to-reminder | Action items to reminders | `/inbox-to-reminder:scan` |
| travel-agent | Flight research & tracking | Natural language queries |
| apple-pim | Calendar, Reminders, Contacts | `/apple-pim:calendars`, `/apple-pim:reminders` |
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

## License

MIT
