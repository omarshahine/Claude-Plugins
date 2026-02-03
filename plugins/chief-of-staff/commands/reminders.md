---
description: Scan inbox for action items and create reminders
argument-hint: "[--from SENDER] [--days N]"
---

# /chief-of-staff:reminders

Scan your inbox for action items and create reminders in Apple Reminders.

## Usage

```
/chief-of-staff:reminders                    # Scan inbox for all action items
/chief-of-staff:reminders --from partner     # Filter by sender (uses configured partner name)
/chief-of-staff:reminders --days 14          # Look back 14 days
/chief-of-staff:reminders --bills            # Focus on bills and invoices
```

## Arguments

- **--from SENDER**: Filter emails by sender name or email
- **--days N**: Number of days to look back (default: 7)
- **--bills**: Focus on bills, invoices, and payment-related emails

## What It Does

1. **Scans inbox** for emails with action items (INBOX only)
2. **Identifies tasks** using keywords: please, need to, deadline, due, invoice, etc.
3. **Extracts details**: amounts, dates, reference numbers
4. **Presents options** via AskUserQuestion for selection
5. **Creates reminders** in appropriate lists (Budget & Finances, Travel, Family, etc.)

## Reminder Lists

- **Reminders** - General tasks
- **Budget & Finances** - Bills, invoices, payments
- **Travel** - Flight bookings, hotel reservations
- **Family** - Family-related tasks (uses configured family_list_name)

## Example Output

```
Action Items Found
==================

Found 4 action items in your inbox:

1. Chase Credit Card Statement
   From: alerts@chase.com
   Due: Balance due Feb 1st ($1,234.56)
   Suggested: Budget & Finances, due Jan 30 9am

2. Dentist Appointment Confirmation
   From: office@dentist.com
   Action: Confirm or reschedule by Friday
   Suggested: Reminders, due Thursday 9am

3. Mom - Sunday Dinner
   From: mom@email.com
   Action: RSVP and headcount by Friday
   Suggested: Family, due Friday 9am

4. Annual Report Review
   From: boss@work.com
   Action: Review and provide feedback
   Suggested: Reminders, due next Monday

Which ones would you like me to create reminders for?
```

## Implementation

Use the Task tool to invoke the inbox-to-reminder agent:

```
subagent_type: "chief-of-staff:inbox-to-reminder"
prompt: "Scan inbox for action items and present options for creating reminders. [additional filters based on arguments]"
```
