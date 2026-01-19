---
description: Query Tripsy app for trip and hotel information
---

# Tripsy Query

Query the Tripsy app database for trip planning information.

## Usage

```
/travel-agent:tripsy [command]
```

## Commands

| Command | Description |
|---------|-------------|
| `list` | List upcoming trips |
| `trip "Name"` | Get full trip details |
| `flights` | Upcoming flights across all trips |
| `hotels` | Upcoming hotel stays |

## Examples

- `/travel-agent:tripsy list`
- `/travel-agent:tripsy trip "Japan 2026"`
- `/travel-agent:tripsy hotels`

## Instructions

Delegate to the `tripsy` agent with the user's command:

```
Task(subagent_type="travel-agent:tripsy", prompt="$ARGUMENTS")
```

If no arguments provided, default to listing upcoming trips.
