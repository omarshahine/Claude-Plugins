---
description: Show benefits expiring soon that need to be used
argument-hint: "[days] [--card card-name]"
allowed-tools:
  - Read
---

# Credit Card Benefits Reminder

Show benefits that are expiring soon and need attention.

## Usage

```
/credit-card-benefits:remind [days] [--card card-name]
```

### Arguments

- **days** (optional): Number of days to look ahead (default: 30)
- **--card** (optional): Filter to specific card

## Logic

1. Read the checklist data
2. For each card and benefit:
   - Calculate the reset date
   - Calculate days until reset
   - Check if benefit has unused balance
3. Filter to benefits expiring within the specified days
4. Sort by urgency (soonest first)

## Reset Date Calculation

### Calendar Year (MM-DD format in resetDate)
- Parse the MM-DD and use current year
- If date has passed this year, it already reset

### Anniversary
- Use accountOpenDate
- Calculate next anniversary from today

### Monthly
- Resets on 1st of next month
- Current month's credit expires end of month

### Quarterly
- Q1: expires Mar 31
- Q2: expires Jun 30
- Q3: expires Sep 30
- Q4: expires Dec 31

## Output Format

```
Expiring Benefits (Next 30 Days)

URGENT (7 days or less):
- Amex Platinum: Resy Q1 - $100 remaining (expires Mar 31, 5 days)
- Delta Reserve: January Rideshare - $10 remaining (expires Jan 31, 9 days)

SOON (8-30 days):
- Chase Sapphire: Exclusive Tables H1 - $150 remaining (expires Jun 30, 28 days)

MONTHLY REMINDERS:
- Amex: Digital Entertainment ($25) - use before month end
- Amex: Uber Cash ($15) - use before month end
- Delta: Resy ($20) - use before month end
```

## Action Suggestions

For each expiring benefit, suggest how to use it:

| Benefit | Suggestion |
|---------|------------|
| Lululemon | Buy yoga pants, workout gear, or gift cards |
| Resy | Book a restaurant reservation this week |
| Saks | Buy something small or a gift card |
| Uber Cash | Take rides or order Uber Eats |
| Entertainment | Sign up for a streaming service |
| Airline Fee | Pay for checked bag or seat selection |

## Examples

```
/credit-card-benefits:remind
/credit-card-benefits:remind 7
/credit-card-benefits:remind 14 --card amex
```
