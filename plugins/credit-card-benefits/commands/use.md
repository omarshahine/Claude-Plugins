---
description: Record usage of a credit card benefit
argument-hint: "<card> <benefit> [amount] [--date YYYY-MM-DD] [--notes 'description']"
allowed-tools:
  - Read
  - Write
  - Edit
---

# Record Credit Card Benefit Usage

Mark a benefit as used (fully or partially) and log the transaction.

## Usage

```
/credit-card-benefits:use <card> <benefit> [amount] [options]
```

### Required Arguments

- **card**: Card name (supports aliases)
- **benefit**: Benefit identifier (see below)

### Optional Arguments

- **amount**: Dollar amount used (defaults to full benefit amount)
- **--date**: Transaction date (defaults to today)
- **--notes**: Description of the transaction

## Benefit Identifiers

### Amex Platinum
- `hotel` or `hotel-h1`, `hotel-h2`
- `resy` or `resy-q1`, `resy-q2`, `resy-q3`, `resy-q4`
- `entertainment` or `digital`
- `lululemon` or `lulu-q1`, `lulu-q2`, `lulu-q3`, `lulu-q4`
- `uber` or `uber-cash`
- `uber-one`
- `airline`
- `saks` or `saks-h1`, `saks-h2`
- `equinox`
- `clear`
- `global-entry` or `tsa`

### Capital One Venture X
- `travel` or `travel-credit`
- `miles` or `anniversary-miles`
- `global-entry` or `tsa`

### Chase Sapphire Reserve
- `travel` or `travel-credit`
- `edit` or `edit-h1`, `edit-h2`
- `dining` or `tables-h1`, `tables-h2`
- `select-hotels` (2026 only)
- `global-entry` or `tsa`

### Alaska Atmos Summit
- `lounge` or `lounge-pass`
- `companion` or `companion-fare`
- `status-points`

### Delta Reserve
- `resy`
- `rideshare`
- `uber-one`
- `delta-stays` or `stays`
- `companion`
- `sky-club` or `skyclub`
- `mqd` or `headstart`
- `global-entry` or `tsa`

## Examples

```
# Used full Lululemon Q1 credit
/credit-card-benefits:use amex lululemon

# Used partial Resy credit
/credit-card-benefits:use amex resy 75 --notes "Dinner at Carbone"

# Used lounge pass on specific date
/credit-card-benefits:use alaska lounge --date 2026-01-15

# Used Venture X travel credit
/credit-card-benefits:use venture-x travel 250 --notes "Flight to NYC"
```

## Behavior

1. Read the current checklist
2. Find the specified card and benefit
3. Update the `used` amount or mark as complete
4. Add transaction to the transactions array (if applicable)
5. Update `lastUpdated` timestamp
6. Save the checklist
7. Display confirmation with:
   - Amount used
   - Remaining balance
   - Days until reset

## Monthly Benefits

For monthly credits (entertainment, uber, etc.), mark the current month as used:
```json
"monthsUsed": [1, 2, 3]  // January, February, March
```

## Validation

- Don't allow usage exceeding the benefit amount
- Warn if benefit appears already fully used
- Warn if benefit period has passed (e.g., using Q1 credit in Q2)
