---
description: Set vacation delivery holds on USPS, UPS, and FedEx
argument-hint: "[start date] [end date]"
---

# /chief-of-staff:package-pause

Set vacation delivery holds across USPS, UPS, and FedEx before a trip.

## Usage

```
/chief-of-staff:package-pause                        # Interactive — asks for dates
/chief-of-staff:package-pause March 1 March 10       # Pre-filled dates
/chief-of-staff:package-pause 2026-03-01 2026-03-10  # ISO format dates
```

## What It Does

1. **Collects dates** — vacation start and end (from arguments or interactively)
2. **Validates duration** — warns if >14 days (UPS/FedEx limit)
3. **Selects carriers** — USPS, UPS, FedEx (user can deselect any)
4. **Automates each carrier** via Playwright:
   - Navigates to carrier's vacation hold page
   - Pauses for manual login if needed
   - Fills in dates
   - Screenshots form for review
   - Submits after user confirmation
5. **Reports results** — success/failure/skipped per carrier

## Carrier Limits

| Carrier | Max Hold | Notes |
|---------|----------|-------|
| USPS | 30 days | Submit by 3 AM ET on start date |
| UPS | 14 days | 6-day gap between consecutive holds |
| FedEx | 14 days | Express + Ground only |

## Implementation

Use the Task tool to invoke the package-pause agent:

```
subagent_type: "chief-of-staff:package-pause"
prompt: "Set vacation delivery holds. {arguments if provided}"
```

If the user provided dates as arguments, pass them in the prompt:
```
prompt: "Set vacation delivery holds from {start_date} to {end_date}."
```
