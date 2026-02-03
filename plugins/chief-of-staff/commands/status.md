---
description: Show unified dashboard of inbox and pending tasks
---

# /chief-of-staff:status

Show a quick dashboard of your inbox status, pending actions, and recent activity.

## Usage

```
/chief-of-staff:status
```

## What It Shows

1. **Inbox Overview**: Unread count, emails by category
2. **Pending Actions**: Emails needing attention
3. **Integration Status**: Parcel deliveries, upcoming reminders
4. **Recent Activity**: Last triage session summary

## Example Output

```
Chief-of-Staff Status
=====================

## Inbox Overview
- Unread: 23 emails
- Top of Mind: 3 (action items detected)
- Newsletters: 8 (suggest unsubscribe)
- Shipping: 2 (packages to track)
- Archive Ready: 10 (high-confidence matches)

## Pending Actions
- 2 packages ready to add to Parcel
- 3 emails with action items (reminders suggested)
- 1 repeat offender newsletter (unsubscribed before)

## Active Deliveries (Parcel)
- FedEx: Arriving tomorrow (B&H Photo)
- UPS: Out for delivery (Amazon)
- USPS: In transit (Etsy)

## Upcoming Reminders
- Today: Pay Chase credit card
- Tomorrow: Call dentist
- Friday: RSVP for dinner

## Recent Activity
Last triage: Feb 1, 2026 at 10:30 AM
- 15 emails processed
- 8 archived, 4 deleted, 2 reminders, 1 kept
- Suggestion accuracy: 87%

## Quick Actions
1. /chief-of-staff:triage - Process inbox
2. /chief-of-staff:parcel - Add packages to Parcel
3. /chief-of-staff:reminders - Create reminders
```

## Implementation

This command performs a quick scan without using a sub-agent:

1. Read `data/settings.yaml` for provider config
2. Load email tools with ToolSearch
3. Call `list_mailboxes` to get Inbox ID
4. Call `advanced_search` for recent unread emails
5. Classify emails using patterns from templates/
6. Load `data/interview-state.yaml` for last session
7. Optionally call Parcel API for active deliveries
8. Optionally call Apple PIM for upcoming reminders
9. Format and display dashboard
