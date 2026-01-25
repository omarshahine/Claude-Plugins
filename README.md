# Agent-Plugins

A personal plugin marketplace for Claude Code. Contains reusable plugins that can be shared across projects and machines.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add omarshahine/Agent-Plugins
```

Then install plugins:

```bash
/plugin install travel-agent@omarshahine-agent-plugins
/plugin install rename-agent@omarshahine-agent-plugins
/plugin install apple-pim@omarshahine-agent-plugins
/plugin install credit-card-benefits@omarshahine-agent-plugins
/plugin install inbox-to-reminder@omarshahine-agent-plugins
/plugin install newsletter-unsubscriber@omarshahine-agent-plugins
/plugin install inbox-to-parcel@omarshahine-agent-plugins
```

## Available Plugins

| Plugin | Description |
|--------|-------------|
| [travel-agent](#travel-agent) | Flight research and trip tracking (Google Flights, ITA Matrix, Flighty, Tripsy) |
| [rename-agent](#rename-agent) | AI-powered file renaming with pattern-based naming |
| [apple-pim](#apple-pim) | Native macOS Calendar, Reminders, and Contacts integration |
| [credit-card-benefits](#credit-card-benefits) | Track and maximize premium credit card benefits and statement credits |
| [inbox-to-reminder](#inbox-to-reminder) | Scan inbox for action items and create Apple Reminders |
| [newsletter-unsubscriber](#newsletter-unsubscriber) | Find and unsubscribe from unwanted newsletters |
| [inbox-to-parcel](#inbox-to-parcel) | Process shipping emails and add tracking to Parcel app |

---

## travel-agent

Reusable travel-related agents for flight research and trip tracking.

### Agents Overview

| Agent | Type | Model | Description |
|-------|------|-------|-------------|
| `google-flights` | Browser automation | sonnet | Search Google Flights for airfare pricing |
| `ita-matrix` | Browser automation (headed) | sonnet | Advanced fare research with detailed pricing rules |
| `flighty` | Local database query | haiku | Query Flighty app for flight tracking data |
| `tripsy` | Local database query | haiku | Query Tripsy app for trip planning data |

### google-flights

**Purpose:** Search Google Flights for airfare pricing estimates using Playwright browser automation.

**Best for:**
- Estimating airfare costs for trip budgeting
- Comparing prices across different dates
- Finding routing options for complex itineraries
- Quick price comparisons with visual results

**How it works:**
1. Constructs Google Flights URLs with encoded search parameters (faster than UI navigation)
2. Uses headless Playwright to navigate and extract results
3. Supports multi-city, round-trip, and one-way searches
4. All cabin classes: Economy, Premium Economy, Business, First

**Example use:**
```
Search business class flights from Seattle to Hong Kong for December 2026
```

**Requirements:**
- `fast-flights` Python library:
  ```bash
  pip install fast-flights
  ```

### ita-matrix

**Purpose:** Search ITA Matrix for detailed fare information, routing rules, and pricing breakdowns.

**Best for:**
- Fare class and booking code research
- Understanding complex routing rules
- Detailed price breakdowns with taxes/fees
- Multi-city itineraries with specific constraints
- Finding the cheapest fare basis codes

**How it works:**
1. Builds JSON search payload and encodes it for URL
2. Uses **headed** Playwright (ITA blocks headless browsers)
3. Requires manual trigger workaround (click "Modify search" then "Search")
4. Searches take 2-5 minutes (this is normal)
5. Extracts detailed fare information from results

**Example use:**
```
Search ITA Matrix for Seattle to Tokyo round-trip in business class, November 2026
```

**Requirements:**
- Playwright MCP plugin (headed - required, ITA blocks headless browsers):
  ```
  /plugin install playwright@claude-plugins-official
  ```

**Note:** ITA Matrix is research-only and doesn't book flights. Use the fare information to book directly with airlines or OTAs.

### flighty

**Purpose:** Query the Flighty app's local database for detailed flight tracking information.

**Best for:**
- Checking your upcoming flights
- Finding seat assignments and aircraft types
- Looking up confirmation codes
- Viewing terminal and gate information
- Flight statistics and history

**How it works:**
1. Runs a Python script that queries Flighty's local SQLite database
2. Returns structured JSON with rich flight data
3. Presents results as formatted markdown tables

**Available commands:**
| Command | Description |
|---------|-------------|
| `list [limit]` | List upcoming flights |
| `next` | Get next upcoming flight |
| `date YYYY-MM-DD` | Flights on a specific date |
| `pnr CODE` | Search by confirmation code |
| `stats` | Flight statistics |
| `recent [limit]` | Past flights |

**Example use:**
```
What's my next flight?
Show me my flight statistics
```

**Requirements:**
- Flighty app installed on macOS
- Database location: `~/Library/Containers/com.flightyapp.flighty/Data/Documents/MainFlightyDatabase.db`

### tripsy

**Purpose:** Query the Tripsy app's local database for trip planning information.

**Best for:**
- Viewing upcoming trips and itineraries
- Checking hotel reservations
- Reviewing planned activities
- Getting trip overviews with all components

**How it works:**
1. Runs a Python script that queries Tripsy's local SQLite database
2. Returns structured JSON with trip, flight, hotel, and activity data
3. Presents results as formatted markdown tables

**Available commands:**
| Command | Description |
|---------|-------------|
| `list [limit]` | List upcoming trips |
| `trip "Name"` | Get full trip details (flights, hotels, activities) |
| `flights [limit]` | Upcoming flights across all trips |
| `hotels [limit]` | Upcoming hotel stays |

**Example use:**
```
What trips do I have coming up?
Show me the details for my Japan trip
```

**Requirements:**
- Tripsy app installed on macOS
- Database location: `~/Library/Group Containers/group.app.tripsy.ios/Tripsy.sqlite`

---

## rename-agent

AI-powered file renaming for Claude Code. Analyzes documents (PDFs, images, text files), classifies them, and applies consistent naming patterns.

**Features:**
- Document analysis (PDFs, images, text files)
- Smart classification (15+ document types)
- Pattern-based naming with tokens
- Pattern learning for reuse
- Batch processing

**Example use:**
```
/rename-agent:rename ~/Downloads/tax-docs
/rename-agent:rename ~/Documents/receipts --pattern "{Date:YYYY-MM-DD} - {Merchant}"
```

Or just ask:
```
Rename the tax documents in my Downloads folder
Help me organize these receipts
```

**Pattern tokens:** `{Date:YYYY-MM-DD}`, `{Year}`, `{Merchant}`, `{Amount}`, `{Institution}`, `{Form Type}`, `{Last 4 Digits}`, `{Description}`

**Document types:** Receipt, Bill, Tax Document, Bank Statement, Invoice, Contract, Medical, Insurance, Investment, Payslip, Identity, Correspondence, Manual, Photo, General

**Requirements:**
- Python 3.10+
- `ANTHROPIC_API_KEY` environment variable
- Install CLI:
  ```bash
  pip install claude-rename-agent
  ```

**Source:** https://github.com/omarshahine/claude-rename-agent

---

## apple-pim

Native macOS integration for Calendar, Reminders, and Contacts using EventKit and Contacts frameworks.

### Features

- **Calendar Management**: Full CRUD operations for calendar events
- **Reminder Management**: Manage reminders with priorities, due dates, and completion tracking
- **Contact Management**: Search, view, and manage contacts with full details
- **Flexible Date Ranges**: Use `lastDays`/`nextDays` or explicit `from`/`to` dates
- **Natural Language**: Accepts dates like "tomorrow", "next Tuesday", "in 2 hours"
- **MCP Integration**: Runs as an MCP server for direct tool access

### Components

| Component | Purpose |
|-----------|---------|
| `pim-assistant` agent | Natural language assistant for PIM operations |
| `apple-pim` skill | EventKit/Contacts framework knowledge |
| Slash commands | `/apple-pim:calendars`, `/apple-pim:reminders`, `/apple-pim:contacts` |
| MCP server | Native Swift CLIs wrapped in Node.js MCP |

### Installation

1. Install the plugin:
   ```bash
   /plugin install apple-pim@omarshahine-agent-plugins
   ```

2. Run the setup script to build Swift CLIs and install dependencies:
   ```bash
   ~/.claude/plugins/cache/omarshahine-agent-plugins/apple-pim/setup.sh
   ```

3. Restart Claude Code to load the MCP server.

### Usage

**Via slash commands:**
```
/apple-pim:calendars events
/apple-pim:calendars create "Team Meeting" --start "tomorrow 2pm" --duration 60
/apple-pim:reminders items --list "Shopping"
/apple-pim:reminders create "Buy milk" --due "tomorrow"
/apple-pim:contacts search "John"
```

**Via natural language (uses pim-assistant agent):**
```
Schedule a meeting with the team for next Tuesday at 2pm
Remind me to call the dentist tomorrow
What's on my calendar this week?
Find John's phone number
```

**Via MCP tools directly:**
```
mcp__apple-pim__calendar_events(lastDays=7, nextDays=14)
mcp__apple-pim__reminder_create(title="Buy groceries", due="tomorrow 5pm", list="Shopping")
mcp__apple-pim__contact_search(query="John")
```

### Slash Commands

| Command | Description |
|---------|-------------|
| `/apple-pim:calendars` | Manage calendar events (list, events, search, create, update, delete) |
| `/apple-pim:reminders` | Manage reminders (lists, items, search, create, complete, update, delete) |
| `/apple-pim:contacts` | Manage contacts (groups, list, search, get, create, update, delete) |

### Available MCP Tools

**Calendar:**
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `calendar_list` | List all calendars | - |
| `calendar_events` | List events in date range | `calendar`, `from`/`to` OR `lastDays`/`nextDays`, `limit` |
| `calendar_get` | Get single event by ID | `id` |
| `calendar_search` | Search events | `query`, `calendar`, `from`, `to`, `limit` |
| `calendar_create` | Create new event | `title`, `start`, `end`/`duration`, `calendar`, `location`, `notes`, `allDay`, `alarm` |
| `calendar_update` | Update existing event | `id`, `title`, `start`, `end`, `location`, `notes` |
| `calendar_delete` | Delete event | `id` |

**Reminders:**
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `reminder_lists` | List all reminder lists | - |
| `reminder_items` | List reminders | `list`, `completed`, `limit` |
| `reminder_get` | Get single reminder by ID | `id` |
| `reminder_search` | Search reminders | `query`, `list`, `completed`, `limit` |
| `reminder_create` | Create new reminder | `title`, `list`, `due`, `notes`, `priority` (0/1/5/9), `alarm` |
| `reminder_complete` | Mark complete/incomplete | `id`, `undo` |
| `reminder_update` | Update reminder | `id`, `title`, `due`, `notes`, `priority` |
| `reminder_delete` | Delete reminder | `id` |

**Contacts:**
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `contact_groups` | List contact groups | - |
| `contact_list` | List contacts | `group`, `limit` |
| `contact_search` | Search contacts | `query`, `limit` |
| `contact_get` | Get full contact details | `id` |
| `contact_create` | Create new contact | `name`/`firstName`+`lastName`, `email`, `phone`, `organization`, `jobTitle`, `notes` |
| `contact_update` | Update contact | `id`, `firstName`, `lastName`, `email`, `phone`, `organization`, `jobTitle`, `notes` |
| `contact_delete` | Delete contact | `id` |

### Date Range Examples

```
# Explicit dates
calendar_events(from="2024-01-15", to="2024-01-22")

# Relative days (7 days ago to 14 days from now)
calendar_events(lastDays=7, nextDays=14)

# Natural language
calendar_events(from="today", to="next week")
```

### Requirements

- macOS 14+ (Sonoma) recommended
- Xcode Command Line Tools (for Swift compilation)
- Node.js 18+
- Grant Calendar, Reminders, and Contacts access when prompted

### Permissions

On first use, macOS will prompt for access to Calendar, Reminders, and Contacts. Grant access in System Settings > Privacy & Security.

---

## credit-card-benefits

Track and maximize your premium credit card benefits with anniversary-aware checklists, multiple data source support, and automatic transaction matching.

### Supported Cards

| Card | Annual Fee | Reset Type |
|------|------------|------------|
| American Express Platinum | $895 | Calendar Year / Monthly |
| Capital One Venture X | $395 | Account Anniversary |
| Chase Sapphire Reserve | $795 | Mixed (Anniversary + Calendar) |
| Bank of America Alaska Airlines Atmos Summit | $395 | Account Anniversary |
| Delta SkyMiles Reserve | $650 | Mixed (Monthly + Anniversary) |

### Quick Start

```bash
# 1. Install the plugin
/plugin install credit-card-benefits@omarshahine-agent-plugins

# 2. Configure your cards and data source
/credit-card-benefits:configure

# 3. Initial sync pulls 12 months of history to find anniversaries
/credit-card-benefits:sync --full

# 4. Check your benefit status
/credit-card-benefits:status
```

### Data Sources

The plugin supports multiple ways to track your transactions:

| Source | Best For | Setup |
|--------|----------|-------|
| **YNAB MCP** | YNAB users with MCP server | Auto-detected |
| **YNAB API** | YNAB users | Requires API token |
| **CSV Import** | Any card | Download from card website |
| **Manual** | Simple tracking | No external data |

### Commands

| Command | Description |
|---------|-------------|
| `/credit-card-benefits:configure` | Interactive setup for cards and data sources |
| `/credit-card-benefits:sync` | Sync transactions (incremental or full 12-month) |
| `/credit-card-benefits:status` | View all benefits and unused credits |
| `/credit-card-benefits:import` | Import transactions from CSV files |
| `/credit-card-benefits:remind` | Show benefits expiring soon |
| `/credit-card-benefits:use` | Manually record benefit usage |
| `/credit-card-benefits:info` | Show detailed card benefit information |
| `/credit-card-benefits:update` | Research and apply benefit changes from web |

### Key Features

- **Anniversary Detection**: Uses annual fee posting date as the most reliable anniversary indicator
- **Multiple Reset Types**: Calendar year, anniversary, monthly, quarterly, semi-annual
- **Benefit Research**: `/update` command searches official and trusted sources for benefit changes
- **Incremental Sync**: After initial setup, only fetches new transactions
- **YAML Checklist**: Human-readable format with comments for easy manual editing

### Natural Language

The `benefits-tracker` agent can be invoked naturally:

```
What Amex credits do I still need to use?
Show me my unused Chase Sapphire benefits
What benefits are expiring this month?
Check for any new credit card benefits
```

### Benefits by Reset Period

**Monthly (Use Every Month!):**
- Amex: Uber Cash ($15), Entertainment ($25), Equinox ($25)
- Delta: Resy ($20), Rideshare ($10)

**Quarterly:**
- Amex: Resy ($100), Lululemon ($75)

**Semi-Annual:**
- Amex: Hotel ($300), Saks ($50)
- Chase: The Edit ($250), Exclusive Tables ($150)

**Annual:**
- Amex: Airline Fee ($200), CLEAR ($209)
- Venture X: Travel ($300), 10K Miles
- Chase: Travel ($300)
- Delta: Delta Stays ($200), Companion Cert
- Alaska: 8 Lounge Passes, Companion Fare

---

## inbox-to-reminder

Scan your email inbox for action items and create reminders in Apple Reminders.

### Features

- Scans inbox for emails containing action items (bills, tasks, deadlines)
- Identifies different types: bills/payments, meetings, follow-ups, deadlines
- Creates reminders with appropriate due dates and context
- Organizes reminders into the correct lists
- Supports multiple email providers (Fastmail, Gmail, Outlook)
- Customizable for your household (partner name, family list)

### Commands

| Command | Description |
|---------|-------------|
| `/inbox-to-reminder:setup` | Configure email provider and customizations |
| `/inbox-to-reminder:scan` | Scan inbox for action items |

### Requirements

- Email MCP server (Fastmail, Gmail, or Outlook)
- `apple-pim` plugin for Apple Reminders

---

## newsletter-unsubscriber

Scan your inbox for newsletters and help you unsubscribe from unwanted ones.

### Features

- Detects newsletters using RFC 2369 email headers (List-Unsubscribe)
- Maintains an allowlist of newsletters you want to keep
- Tracks previously unsubscribed senders to flag repeat offenders
- Executes unsubscribes via mailto or web forms (Playwright)
- Organizes processed emails to a dedicated folder

### Commands

| Command | Description |
|---------|-------------|
| `/newsletter-unsubscriber:setup` | Configure email provider |
| `/newsletter-unsubscriber:unsubscribe` | Scan and unsubscribe from newsletters |

### Requirements

- Email MCP server (Fastmail, Gmail, or Outlook)
- Playwright plugin (bundled) for web-based unsubscribes

---

## inbox-to-parcel

Process shipping notification emails and add tracking to Parcel app.

### Features

- Scans inbox for shipment notification emails
- Extracts tracking numbers and carrier information
- Adds deliveries to Parcel app via API
- Moves processed emails to the Orders folder
- Handles Amazon emails specially (auto-sync to Parcel)
- Supports UPS, FedEx, USPS, DHL, OnTrac, and more

### Commands

| Command | Description |
|---------|-------------|
| `/inbox-to-parcel:setup` | Configure email and Parcel providers |
| `/inbox-to-parcel:track` | Process shipping emails |

### Requirements

- Email MCP server (Fastmail, Gmail, or Outlook)
- Parcel API MCP server (`npx -y @smithery/cli@latest install @NOVA-3951/parcel-api-mcp --client claude`)
- Playwright plugin (bundled) for web-based tracking extraction

---

## Usage

After installation, use agents via the Task tool:

```
Task(subagent_type="travel-agent:google-flights", prompt="Search business class SEA to HKG Dec 2026")
Task(subagent_type="travel-agent:flighty", prompt="List upcoming flights")
Task(subagent_type="travel-agent:ita-matrix", prompt="Search SEA-NRT round-trip business Nov 2026")
Task(subagent_type="travel-agent:tripsy", prompt="Show my upcoming trips")
Task(subagent_type="apple-pim:pim-assistant", prompt="What's on my calendar this week?")
Task(subagent_type="credit-card-benefits:benefits-tracker", prompt="What credits are expiring this month?")
Task(subagent_type="inbox-to-reminder:inbox-to-reminder", prompt="Scan inbox for action items")
Task(subagent_type="newsletter-unsubscriber:newsletter-unsubscriber", prompt="Scan inbox for newsletters")
Task(subagent_type="inbox-to-parcel:inbox-to-parcel", prompt="Process shipping emails")
```

## Creating New Plugins

1. Create a new directory under `plugins/`
2. Add `.claude-plugin/plugin.json` with metadata
3. Add agents, skills, or commands as needed
4. Register the plugin in `.claude-plugin/marketplace.json`
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

The marketplace is defined in `.claude-plugin/marketplace.json`. Add new plugins to the `plugins` array:

```json
{
  "name": "omarshahine-agent-plugins",
  "plugins": [
    {
      "name": "my-plugin",
      "source": "./plugins/my-plugin",
      "description": "Description of my plugin",
      "version": "1.0.0",
      "keywords": ["keyword1", "keyword2"],
      "category": "productivity"
    }
  ]
}
```

## License

MIT
