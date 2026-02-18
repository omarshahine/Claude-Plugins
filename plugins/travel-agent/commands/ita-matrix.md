---
description: Search ITA Matrix for detailed fare research and pricing rules
---

# ITA Matrix Search

Search ITA Matrix for detailed fare information, booking codes, and pricing rules.

## Usage

```
/travel-agent:ita-matrix [search query]
```

## Examples

- `/travel-agent:ita-matrix SEA-NRT business class November 2026`
- `/travel-agent:ita-matrix DCA to SEA first class April 1-4`
- `/travel-agent:ita-matrix LAX-LHR fare rules and booking codes`

## Instructions

Delegate to the `ita-matrix` agent with the user's search query:

```
Task(subagent_type="travel-agent:ita-matrix", prompt="$ARGUMENTS")
```

If no arguments provided, ask the user for:
- Origin and destination airports
- Travel dates
- Cabin class
- Any specific fare rules or booking code requirements

## Notes

- ITA Matrix requires a headed browser (blocks headless)
- Searches can take 2-5 minutes
- Best for complex fare research, not quick price checks
