# Agent-Plugins

A personal plugin marketplace for Claude Code. Contains reusable plugins that can be shared across projects and machines.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add omarshahine/Agent-Plugins
```

Then install plugins:

```bash
/plugin install travel-agent@agent-plugins
```

## Available Plugins

### travel-agent

Reusable travel-related agents for flight research and trip tracking.

#### Agents Overview

| Agent | Type | Model | Description |
|-------|------|-------|-------------|
| `google-flights` | Browser automation | sonnet | Search Google Flights for airfare pricing |
| `ita-matrix` | Browser automation (headed) | sonnet | Advanced fare research with detailed pricing rules |
| `flighty` | Local database query | haiku | Query Flighty app for flight tracking data |
| `tripsy` | Local database query | haiku | Query Tripsy app for trip planning data |

---

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
- Playwright MCP server (headless)
  ```bash
  claude mcp add --scope user playwright -- npx -y @playwright/mcp@latest --headless --browser msedge
  ```

---

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
- Playwright MCP server (headed - required, ITA blocks headless)
  ```bash
  claude mcp add --scope user plugin_playwright_playwright -- npx -y @anthropic/claude-code-mcp-plugin-playwright@latest
  ```

**Note:** ITA Matrix is research-only and doesn't book flights. Use the fare information to book directly with airlines or OTAs.

---

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

---

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

## Usage

After installation, use agents via the Task tool:

```
Task(subagent_type="travel-agent:google-flights", prompt="Search business class SEA to HKG Dec 2026")
Task(subagent_type="travel-agent:flighty", prompt="List upcoming flights")
Task(subagent_type="travel-agent:ita-matrix", prompt="Search SEA-NRT round-trip business Nov 2026")
Task(subagent_type="travel-agent:tripsy", prompt="Show my upcoming trips")
```

## Creating New Plugins

1. Create a new directory under `plugins/`
2. Add `.claude-plugin/plugin.json` with metadata
3. Add agents, skills, or commands as needed
4. Update this README

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

## License

MIT
