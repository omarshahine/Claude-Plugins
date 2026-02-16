---
description: |
  Real-time aircraft tracking using the official FlightRadar24 API.
  Use when the user asks where a plane is, wants to track a flight by tail number or callsign,
  check aircraft status, or get recent flight history for a specific aircraft.
---

# Flight Radar

Track aircraft in real-time using the official FlightRadar24 API via MCP tools.

## Setup

Use `ToolSearch` to load the FR24 MCP tools:

```
ToolSearch query: "+fr24api"
```

This loads all available FR24 tools. Key tools:

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `get_live_flights_positions_full` | Real-time position by registration or callsign | `registrations`, `callsigns`, `flights` (arrays) |
| `get_flight_summary_full` | Recent flight history with departure/arrival details | `flights` (array of flight numbers/callsigns) |
| `get_flight_tracks` | Detailed positional track for a specific flight | `flight_id` |
| `get_airline_info` | Airline details by ICAO/IATA code | `code` |
| `get_airport_info_full` | Airport details and stats | `code` |

## Workflow

### Track by tail number (registration)

1. Load tools: `ToolSearch` with `+fr24api`
2. Call `get_live_flights_positions_full` with `registrations: ["N464QS"]`
3. If found, present position, altitude, speed, heading, route
4. For flight history, call `get_flight_summary_full` with the callsign from step 2

### Track by callsign or flight number

1. Load tools: `ToolSearch` with `+fr24api`
2. Call `get_live_flights_positions_full` with `callsigns: ["EJA464"]` or `flights: ["EJA464"]`
3. Present the results

### Get flight history

1. Load tools: `ToolSearch` with `+fr24api`
2. Call `get_flight_summary_full` with the flight number or callsign

## Response Format

Present results clearly with:
- Registration, callsign, aircraft type
- Route (origin → destination) with airport names
- Position (lat/lon), altitude, ground speed, heading
- Status (in flight, landed, on ground)
- Departure/arrival times or ETA

## Visual Map

To show the user a map, pipe FR24 data through `flight-map.py`:

```bash
echo '<JSON>' | python3 scripts/flight-map.py --stdin
```

The JSON should contain these fields (matching the map template):

```json
{
  "registration": "N464QS",
  "callsign": "EJA464",
  "aircraft_model": "Embraer Phenom 300E",
  "aircraft_type": "E55P",
  "airline": "NetJets",
  "latitude": 37.1234,
  "longitude": -122.5678,
  "altitude_ft": 35000,
  "ground_speed_kts": 420,
  "heading": 270,
  "on_ground": false,
  "origin": "TEB",
  "origin_city": "Teterboro",
  "destination": "SFO",
  "destination_city": "San Francisco",
  "flight_status": "En Route",
  "actual_departure": "2025-01-15 14:30 UTC",
  "eta": "2025-01-15 20:15 UTC",
  "recent_flights": [
    {
      "origin": "TEB",
      "origin_city": "Teterboro",
      "destination": "SFO",
      "destination_city": "San Francisco",
      "departure": "2025-01-14 08:00 UTC"
    }
  ]
}
```

Map to these fields from the FR24 MCP tool responses. If a field isn't available, omit it — the map handles missing values gracefully.

```bash
# Save to a specific file
echo '<JSON>' | python3 scripts/flight-map.py --stdin --output map.html

# Generate without opening browser
echo '<JSON>' | python3 scripts/flight-map.py --stdin --no-open
```

The map shows:
- Dark basemap (CARTO dark tiles) with aircraft icon rotated to heading
- Info panel with route, altitude, speed, heading, departure/ETA
- Recent flights table (if available)
- Auto-adjusting zoom (z6 for cruise, z10 for low altitude, z13 on ground)

If the aircraft data has `status: "not_found"` or is empty, it renders a styled "not tracked" card.

## Limitations

- **Live only**: FlightRadar24 tracks aircraft with active ADS-B transponders. Parked/powered-down aircraft won't appear in live positions.
- **No future flights**: Scheduled/upcoming flights are not available. Charter and private flights don't publish schedules publicly.
- **API quota**: The official API has rate limits based on the subscription tier. Avoid unnecessary repeated calls.
