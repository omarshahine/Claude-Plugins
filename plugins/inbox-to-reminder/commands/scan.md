---
description: Scan inbox for action items and create reminders
---

# /inbox-to-reminder:scan

Scan your email inbox for action items, bills, deadlines, and tasks, then create reminders.

## Usage

```
/inbox-to-reminder:scan                    # Scan recent inbox (7 days)
/inbox-to-reminder:scan partner            # Scan emails from partner
/inbox-to-reminder:scan --days 30          # Scan last 30 days
/inbox-to-reminder:scan bills              # Search for bills/invoices
```

## Arguments

- **sender** (optional): Filter by sender name or email
- **--days N**: Number of days to look back (default: 7)
- **query**: Search term to filter emails

## What It Does

1. **Scans** inbox for emails containing action items
2. **Identifies** tasks, bills, deadlines, and follow-ups
3. **Presents** found items for your selection
4. **Creates** reminders in the appropriate lists:
   - Budget & Finances (bills, payments)
   - Travel (bookings, reservations)
   - Family (family tasks)
   - Reminders (general)

## Types of Action Items Detected

- **Bills/Payments**: Invoices, statements, payment due dates
- **Meetings/Events**: RSVPs, calendar items, scheduling requests
- **Tasks**: To-dos, follow-ups, things to complete
- **Deadlines**: Time-sensitive items with specific due dates
- **Administrative**: Forms to fill, documents to sign, registrations

## Example Output

```
Found 3 action items in your inbox:

1. [BILL] Chase Credit Card Statement
   From: chase.com
   Due: January 25, 2026
   Amount: $1,234.56
   -> Create reminder in Budget & Finances?

2. [TASK] Review and sign insurance documents
   From: Family Member
   Mentioned: "please review when you get a chance"
   -> Create reminder in Family?

3. [DEADLINE] Quarterly tax payment
   From: notifications@irs.gov
   Due: January 15, 2026 (OVERDUE)
   -> Create reminder in Budget & Finances?

Select items to create reminders for: [1, 2, 3]
```

## Implementation

Use the Task tool to invoke the inbox-to-reminder agent:

```
subagent_type: "inbox-to-reminder:inbox-to-reminder"
prompt: "Scan inbox for action items and create reminders. Filter: [arguments]"
```
