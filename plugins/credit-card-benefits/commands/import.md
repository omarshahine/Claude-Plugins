---
description: Import transactions from CSV to match against credit card benefits
argument-hint: "<file.csv> [--card card-name] [--format amex|chase|capital-one|ynab]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
---

# Import Transactions from CSV

Import credit card transactions from CSV files to automatically match against benefits and identify statement credits.

## Usage

```
/credit-card-benefits:import <file.csv> [--card card-name] [--format format]
```

### Arguments

- **file.csv** (required): Path to the CSV file
- **--card** (optional): Which card these transactions are from
- **--format** (optional): CSV format hint (auto-detected if not specified)

## Supported Formats

### American Express
```csv
Date,Description,Amount
01/15/2026,UBER EATS,-25.00
01/15/2026,STATEMENT CREDIT,15.00
```

Columns: Date, Description, Card Member, Account #, Amount (or Reference, Amount)

### Chase
```csv
Transaction Date,Post Date,Description,Category,Type,Amount
01/15/2026,01/16/2026,LYFT *RIDE,Travel,Sale,-25.00
01/16/2026,01/17/2026,SAPPHIRE RESERVE CREDIT,Rewards,Payment,25.00
```

### Capital One
```csv
Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit
01/15/2026,01/16/2026,1234,CAPITAL ONE TRAVEL,Travel,300.00,
01/16/2026,01/17/2026,1234,TRAVEL CREDIT,Rewards,,300.00
```

### YNAB Export
```csv
Account,Date,Payee,Category,Memo,Outflow,Inflow
Amex Platinum,01/15/2026,Uber Eats,Restaurants,,25.00,
Amex Platinum,01/16/2026,Statement Credit,,,15.00
```

### Generic CSV
Must have at minimum: Date, Description/Payee, Amount columns

## Auto-Detection Logic

The importer will:
1. Read the CSV header row
2. Identify the format based on column names
3. Parse dates (handles MM/DD/YYYY, YYYY-MM-DD, etc.)
4. Normalize amounts (handle negative vs positive conventions)

## Matching Logic

### Benefit Transactions
Match purchases to benefits based on merchant patterns:

| Pattern | Benefit | Card |
|---------|---------|------|
| UBER, UBER EATS | Uber Cash | Amex Platinum |
| LULULEMON | Lululemon Credit | Amex Platinum |
| SAKS, SAKSFIFTHAVENUE | Saks Credit | Amex Platinum |
| DISNEY, HULU, ESPN+ | Entertainment | Amex Platinum |
| EQUINOX | Equinox Credit | Amex Platinum |
| RESY, known Resy restaurants | Resy Credit | Amex Platinum, Delta |
| LYFT, UBER (rides) | Rideshare Credit | Delta Reserve |
| CAPITAL ONE TRAVEL | Travel Credit | Venture X |
| CHASE TRAVEL | Travel/Hotel Credit | Sapphire Reserve |
| DELTA.COM/STAYS | Delta Stays | Delta Reserve |

### Statement Credits
Identify credits by:
- Negative amounts (outflow) or Credit column populated
- Keywords: CREDIT, STATEMENT CREDIT, REWARD, BONUS
- Match timing to recent purchases (1-5 days later)

### Annual Fee Detection
Look for transactions matching:
- "ANNUAL FEE", "ANNUAL MEMBERSHIP FEE", "YEARLY FEE"
- Amount matching known annual fees ($895, $795, $650, $395)
- Use posting date as the card anniversary date

## Output

After import, display:

```
Import Summary: amex-january-2026.csv
=====================================

Transactions Processed: 150
Date Range: 2026-01-01 to 2026-01-31

BENEFIT MATCHES FOUND:
- Jan 5: UBER EATS $18.50 → Uber Cash (Jan)
- Jan 8: LULULEMON $89.00 → Lululemon Q1
- Jan 12: DISNEY PLUS $15.99 → Entertainment (Jan)
- Jan 15: CARBONE NYC $125.00 → Resy Q1

STATEMENT CREDITS FOUND:
- Jan 6: UBER CASH CREDIT $15.00 ✓
- Jan 9: LULULEMON CREDIT $75.00 ✓
- Jan 13: ENTERTAINMENT CREDIT $15.99 ✓

ANNUAL FEE DETECTED:
- Jan 15: ANNUAL MEMBERSHIP FEE $895.00
  → Setting card anniversary to January 15

UNMATCHED CREDITS (review manually):
- Jan 20: STATEMENT CREDIT $50.00 → Unknown source

Update checklist with these matches? [y/n]
```

## Data Updates

When confirmed, the importer will:
1. Update `used` amounts for matched benefits
2. Add transactions to the transaction arrays
3. Update `accountOpenDate` if annual fee detected
4. Update `lastAnnualFeeDate` for tracking
5. Save changes to checklist.yaml

## Example Transaction Entry

```yaml
transactions:
  - date: 2026-01-08
    amount: 89.00
    merchant: LULULEMON
    creditReceived: 75.00
    creditDate: 2026-01-09
    importedFrom: amex-january-2026.csv
```

## Tips

1. **Download statements monthly** to keep tracking current
2. **Use card-specific exports** for best matching accuracy
3. **Review unmatched credits** - they may be benefits you forgot about
4. **Annual fee date** is the most reliable anniversary indicator
