# travel-agent Plugin

Reusable travel agents for flight research and tracking.

## Agents

| Agent | Description | Model |
|-------|-------------|-------|
| `google-flights` | Search Google Flights for airfare pricing estimates | sonnet |
| `ita-matrix` | Search ITA Matrix for detailed fare codes, rules, pricing | sonnet |
| `flighty` | Query Flighty app database for flight tracking data | haiku |
| `tripsy` | Query Tripsy app database for trip/hotel information | haiku |

## Installation

```bash
claude plugin install claude-plugins:travel-agent
```

## Usage

Use agents via the Task tool with qualified names:

```python
# Search for flights
Task(subagent_type="travel-agent:google-flights", prompt="Search business class SEA to HKG Dec 26-Jan 3 2026, 4 passengers")

# Detailed fare research
Task(subagent_type="travel-agent:ita-matrix", prompt="Search ITA Matrix SEA-HKG business Nov 21-28 2026, get fare codes")

# Query flight tracking
Task(subagent_type="travel-agent:flighty", prompt="List upcoming flights")
Task(subagent_type="travel-agent:flighty", prompt="Show flights on 2026-03-15")

# Query trip data
Task(subagent_type="travel-agent:tripsy", prompt="List upcoming trips")
Task(subagent_type="travel-agent:tripsy", prompt="Get details for Japan trip")
```

## Requirements

### For google-flights

- **fast-flights** Python library:
  ```bash
  pip install fast-flights
  ```

### For ita-matrix

- **Playwright MCP server** configured (ITA Matrix requires headed browser):
  ```bash
  claude mcp add --scope user plugin_playwright_playwright -- npx -y @anthropic/claude-code-mcp-plugin-playwright@latest
  ```

### For flighty

- **Flighty app** installed with data at:
  `~/Library/Containers/com.flightyapp.flighty/Data/Documents/MainFlightyDatabase.db`

### For tripsy

- **Tripsy app** installed with data at:
  `~/Library/Group Containers/group.app.tripsy.ios/Tripsy.sqlite`

## Agent Details

### google-flights

Uses the [fast-flights](https://github.com/AWeirdDev/flights) library to search Google Flights. Supports:
- Multi-city itineraries
- Round-trip and one-way searches
- All cabin classes (Economy, Premium Economy, Business, First)
- Multiple passengers

Fast and reliable - no browser automation required. Best for quick price comparisons and availability checks.

### ita-matrix

Uses headed Playwright to search ITA Matrix. Supports:
- Fare class/booking code research
- Complex routing rules
- Detailed fare breakdowns
- Multi-city with constraints

Better than Google Flights for understanding fare structures. Note: Searches take 2-5 minutes.

### flighty

Queries the Flighty macOS app database for:
- Upcoming flights with full details
- Seat assignments and cabin class
- Aircraft type and registration
- Terminal and gate information
- Confirmation codes

### tripsy

Queries the Tripsy macOS app database for:
- Upcoming trips with dates
- Hotel reservations
- Activity bookings
- Flight information (basic)

## License

MIT
