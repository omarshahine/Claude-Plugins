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
## Inbox Overview
- **Total**: 28 emails
- **Unread**: 23 emails
- **Threads**: 26

### Email Categories
| Type | Count | Examples |
|------|-------|----------|
| Shipping/Orders | 3 | Home Depot, Amazon |
| Newsletters | 8 | Tech Digest, Cooking Weekly |
| Personal | 4 | Travel Agency, Family |
| Actionable | 3 | Product return, Club check-in |

## Active Deliveries (Parcel)
| Carrier | Item | Status | Expected |
|---------|------|--------|----------|
| USPS | Cadence Spatula | In transit | Today |
| FedEx | Watch Tools | In transit | Tomorrow |
| Amazon | Soap | Out for delivery | Jan 29 |

## Upcoming Reminders
| Reminder | Due |
|----------|-----|
| Pay Chase credit card | Today |
| Call dentist | Tomorrow |
| RSVP for dinner | Friday |

## Mailbox Summary
| Folder | Unread |
|--------|--------|
| Inbox | 24 |
| Orders | 222 |
| Financial Alerts | 146 |
| Bills | 18 |

## Quick Actions
1. `/chief-of-staff:triage` - Process inbox
2. `/chief-of-staff:parcel` - Add packages to Parcel
3. `/chief-of-staff:reminders` - Create reminders
```

**Note**: Do NOT use emojis in table cells - they break column alignment in terminal rendering. Emojis in headers and lists are fine.

## Implementation

This command performs a quick scan without using a sub-agent:

1. Read `~/.claude/data/chief-of-staff/settings.yaml` for provider config
2. Load email tools with ToolSearch
3. Call `list_mailboxes` to get Inbox ID
4. Call `advanced_search` for recent unread emails
5. Classify emails using patterns from assets/ (use Glob to find in plugin cache)
6. Load `~/.claude/data/chief-of-staff/interview-state.yaml` for last session
7. Optionally call Parcel API for active deliveries
8. Optionally call Apple PIM for upcoming reminders
9. Format and display dashboard
