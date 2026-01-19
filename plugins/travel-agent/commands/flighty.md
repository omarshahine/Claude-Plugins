---
description: Query Flighty app for flight tracking information
---

# Flighty Query

Query the Flighty app database for flight tracking information.

## Usage

```
/travel-agent:flighty [command]
```

## Commands

| Command | Description |
|---------|-------------|
| `list` | List upcoming flights |
| `next` | Get next upcoming flight |
| `date YYYY-MM-DD` | Flights on a specific date |
| `pnr CODE` | Search by confirmation code |
| `stats` | Flight statistics |
| `recent` | Past flights |

## Examples

- `/travel-agent:flighty list`
- `/travel-agent:flighty next`
- `/travel-agent:flighty date 2026-04-01`
- `/travel-agent:flighty pnr ABC123`

## Instructions

Delegate to the `flighty` agent with the user's command:

```
Task(subagent_type="travel-agent:flighty", prompt="$ARGUMENTS")
```

If no arguments provided, default to listing upcoming flights.
