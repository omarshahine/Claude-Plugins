---
description: Search Google Flights for airfare pricing estimates
---

# Google Flights Search

Search Google Flights for airfare pricing using the google-flights agent.

## Usage

```
/travel-agent:google-flights [search query]
```

## Examples

- `/travel-agent:google-flights SEA to HKG business class December 2026`
- `/travel-agent:google-flights round-trip NYC to London first class March 15-22`
- `/travel-agent:google-flights multi-city SEA-TYO-HKG-SEA premium economy`

## Instructions

Delegate to the `google-flights` agent with the user's search query:

```
Task(subagent_type="travel-agent:google-flights", prompt="$ARGUMENTS")
```

If no arguments provided, ask the user for:
- Origin and destination airports
- Travel dates
- Cabin class (economy, premium economy, business, first)
- Trip type (one-way, round-trip, multi-city)
