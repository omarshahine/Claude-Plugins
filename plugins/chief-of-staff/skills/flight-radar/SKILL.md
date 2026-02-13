---
description: |
  Real-time aircraft tracking using FlightRadar24 API.
  Use when the user asks where a plane is, wants to track a flight by tail number or callsign,
  check aircraft status, or get recent flight history for a specific aircraft.
---

# Flight Radar

Track aircraft in real-time using the FlightRadar24 Python API. Returns live position, route, status, aircraft details, and recent flight history.

## Script

`scripts/flight-radar.py` in the plugin directory.

```bash
# Single tail number
python3 scripts/flight-radar.py N12345 --json

# Multiple aircraft
python3 scripts/flight-radar.py N12345 N67890 --json

# Plain text output (no --json flag)
python3 scripts/flight-radar.py N12345

# Poll every 30 seconds (for in-flight tracking)
python3 scripts/flight-radar.py N12345 --poll 30

# All active flights for an airline (EJA = Executive Jet Aviation)
python3 scripts/flight-radar.py --fleet --json
```

## JSON Output Fields

When a flight is found (`status: "tracked"`):

| Field | Description |
|-------|-------------|
| `callsign` | ATC callsign (e.g., "EJA464") |
| `registration` | Tail number (e.g., "N464QS") |
| `aircraft_type` | ICAO type code (e.g., "E55P") |
| `aircraft_model` | Full model name (e.g., "Embraer Phenom 300E") |
| `airline` | Operator name |
| `airline_icao` | ICAO airline code |
| `latitude` / `longitude` | Current position |
| `altitude_ft` | Altitude in feet |
| `ground_speed_kts` | Ground speed in knots |
| `heading` | Track heading in degrees |
| `on_ground` | Whether aircraft is on the ground |
| `origin` / `destination` | IATA airport codes |
| `origin_name` / `destination_name` | Full airport names |
| `origin_city` / `destination_city` | City names |
| `flight_status` | Status text (e.g., "Landed 12:59", "Estimated 14:30", "En Route") |
| `scheduled_departure` / `scheduled_arrival` | Scheduled times (UTC) |
| `actual_departure` / `actual_arrival` | Actual times (UTC) |
| `eta` | Estimated time of arrival (UTC) |
| `recent_flights` | Array of last ~4 flights for this tail |

Each `recent_flights` entry has: `callsign`, `origin`, `origin_city`, `destination`, `destination_city`, `departure`.

When not found (`status: "not_found"`):
```json
{"tail": "N12345", "status": "not_found", "message": "Not currently airborne or not tracked"}
```

## When to Use --poll

Use `--poll 30` when tracking an in-flight aircraft over time. It re-queries every N seconds and prints updated position, altitude, and speed. Useful for "let me know when it lands" — watch for `on_ground: true` or a "Landed" status.

Don't poll for parked/ground aircraft — it wastes API calls and the data won't change.

## When to Use --json

`--json` returns raw structured data including lat/lon coordinates. Use this when:
- You need to parse the response programmatically
- The user wants specific fields (e.g., "what altitude is it at?")
- You're feeding data into another tool or generating a map link

To give the user a quick visual, construct a Google Maps link from the lat/lon:
```
https://www.google.com/maps?q={latitude},{longitude}
```

## Limitations

- **Live only**: FlightRadar24 tracks aircraft with active ADS-B transponders. Parked/powered-down aircraft return "not_found".
- **No future flights**: Scheduled/upcoming flights are not available from this API. Charter and private flights don't publish schedules publicly.
- **History is shallow**: `recent_flights` covers the last ~4 legs only, with departure times but no arrival times.
- **Rate limiting**: The API is unofficial; heavy usage may be throttled.

## Prerequisites

```bash
pip3 install FlightRadarAPI beautifulsoup4
```
