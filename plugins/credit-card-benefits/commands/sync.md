---
description: Sync transactions from configured data source (YNAB or CSV)
argument-hint: "[--full] [--since YYYY-MM-DD]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
---

# Sync Transactions

Fetch new transactions from your configured data source and update benefit tracking.

## Usage

```
/credit-card-benefits:sync [options]
```

### Options

- `--full` - Full 12-month resync (useful if data seems off)
- `--since YYYY-MM-DD` - Sync from specific date
- (no options) - Incremental sync from last sync date

## Execution Steps

When this command runs:

1. **Load configuration** from `~/.config/credit-card-benefits/checklist.yaml`
2. **Load detection patterns** from plugin's `data/benefit-patterns.yaml`
3. **Validate YNAB token** (if using YNAB)
4. **For each enabled card:**
   - Fetch transactions since last sync (or 13 months for `--full`)
   - **Detect annual fee** → Automatically set `anniversaryMonth` and `anniversaryDay`
   - Match transactions to benefits using patterns (payee, memo, category)
   - Identify statement credits received (positive amounts in YNAB)
5. **Update checklist.yaml** with:
   - Anniversary dates discovered from fees
   - Benefit usage status
   - Last sync date
6. **Display summary** of changes

## Benefit Detection Patterns

Patterns are defined in `data/benefit-patterns.yaml` and include:
- **payee**: Merchant name patterns to match
- **memo**: Transaction memo/note patterns
- **category**: YNAB category patterns
- **credit_payee**: Statement credit payee patterns
- **amount_range**: Expected charge amounts
- **credit_amount**: Expected credit amounts

**Note:** Some benefits like Uber Cash are NOT statement credits - they're loaded to external accounts and must be tracked manually.

## How It Works

### Incremental Sync (Default)

Fetches transactions since `config.sync.lastSyncDate`:

```
Last sync: 2026-01-15

Fetching transactions from 2026-01-15 to today...

AMEX PLATINUM (via YNAB)
────────────────────────
New transactions: 12
Benefit matches: 4
Credits received: 3

CHASE SAPPHIRE RESERVE (via YNAB)
─────────────────────────────────
New transactions: 8
Benefit matches: 2
Credits received: 2

Updating checklist...
Done. Next sync will start from 2026-01-22.
```

### Full Sync

Re-fetches 12 months of data:

```
/credit-card-benefits:sync --full

WARNING: This will re-analyze 12 months of transactions.
Existing benefit tracking will be recalculated.

Proceed? [y/n]
```

## Data Source Handling

### YNAB MCP Server

If MCP server is configured and available:

```python
# Pseudo-code for MCP approach
for card in enabled_cards:
    account_id = config.ynab.accountMapping[card]
    transactions = mcp__ynab__get_transactions(
        budget_id=config.ynab.budgetId,
        account_id=account_id,
        since_date=last_sync_date
    )
    process_transactions(card, transactions)
```

### YNAB API

If using direct API:

```bash
TOKEN=$(cat ~/.config/credit-card-benefits/ynab-token)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.youneedabudget.com/v1/budgets/${BUDGET_ID}/accounts/${ACCOUNT_ID}/transactions?since_date=${SINCE_DATE}"
```

### CSV Import

For CSV-based tracking, sync prompts for file import:

```
CSV-based sync requires importing new statement files.

Please download recent statements:
- Amex Platinum: amex.com → Statements & Activity
- Chase Sapphire: chase.com → Activity → Download

Then run:
/credit-card-benefits:import <file.csv> --card <card-name>
```

## Transaction Processing

### 1. Detect Annual Fees & Set Anniversary Month

**This is critical for cardmember-year benefits.** Search for annual fee transactions to automatically set anniversary months.

#### Annual Fee Detection Strategy

**Don't hardcode fee amounts** - they change yearly. Instead, detect by:

1. **Transaction patterns** (payee name, memo, category)
2. **Amount range** ($250-$900 for premium cards)
3. **One per year** per account

#### Detection Patterns

Search for transactions matching ANY of these patterns:

| Field | Patterns to Match (case-insensitive) |
|-------|--------------------------------------|
| Payee name | "annual fee", "membership fee", "annual membership" |
| Memo | "annual fee", "membership fee", "annual membership", "card fee" |
| Category | "annual fee", "membership fee", "credit card fee" |

**Amount filter:** Between $250 and $900 (covers all premium cards with buffer for fee increases)

#### YNAB API Query for Fees

```bash
# Search each mapped account for annual fee transactions
TOKEN=$(cat ~/.config/credit-card-benefits/ynab-token)
BUDGET_ID="<budget-id>"
ACCOUNT_ID="<account-id>"

# Fetch transactions from past 13 months to catch recent anniversary
SINCE_DATE=$(date -v-13m +%Y-%m-%d)

curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.youneedabudget.com/v1/budgets/$BUDGET_ID/accounts/$ACCOUNT_ID/transactions?since_date=$SINCE_DATE" \
  | jq '[.data.transactions[] | select(
      # Amount between $250-$900 (negative in YNAB = charge)
      (.amount < -250000 and .amount > -900000) and
      # Match fee patterns in payee, memo, or category
      (
        (.payee_name // "" | ascii_downcase | test("annual|membership fee")) or
        (.memo // "" | ascii_downcase | test("annual|membership fee|card fee")) or
        (.category_name // "" | ascii_downcase | test("annual|membership|card fee"))
      )
    )] | sort_by(.date) | last | {date, amount: (-.amount/1000), payee: .payee_name, memo, category: .category_name}'
```

**Note:** YNAB amounts are in milliunits (divide by 1000). Negative = charge to card.

#### Automatic Anniversary Detection

When a fee transaction is found, show details so user can verify:

```
Looking for annual fee transactions...

Amex Platinum (b6bf939d-9bba-41fa-bfdd-c2db36e0f445):
  Found fee transaction:
    Date: 2025-11-15
    Amount: $895.00
    Payee: "AMERICAN EXPRESS"
    Memo: "ANNUAL MEMBERSHIP FEE"
    Category: "Credit Card Fees"
  → Setting anniversaryMonth: 11 (November)
  → Card anniversary: November 15th each year

Chase Sapphire Reserve (1cb07ea3-8345-4d3c-bc33-bba7a0bcd679):
  Found fee transaction:
    Date: 2025-08-22
    Amount: $795.00
    Payee: "CHASE CARD SERVICES"
    Memo: "ANNUAL FEE"
    Category: "Subscriptions"
  → Setting anniversaryMonth: 8 (August)
  → Card anniversary: August 22nd each year

Capital One Venture X (8c34a47f-5233-41dc-9123-097acc9f5d20):
  No annual fee found in past 13 months
  → anniversaryMonth: null (set manually or wait for next fee)

  Tip: Check that the fee transaction has "annual" or "membership fee"
  in the payee name, memo, or category in YNAB.
```

#### Update Checklist with Anniversary

```yaml
# Updated in checklist.yaml
benefits:
  amex-platinum:
    anniversaryMonth: 11
    anniversaryDay: 15
    lastAnnualFeeDate: "2025-11-15"
    lastAnnualFeeAmount: 895
    lastAnnualFeePayee: "AMERICAN EXPRESS"
    lastAnnualFeeMemo: "ANNUAL MEMBERSHIP FEE"
    nextAnnualFeeDate: "2026-11-15"
```

This enables proper tracking of cardmember-year benefits (travel credits, companion certificates, etc.) that reset on card anniversary rather than calendar year.

#### Manual Override

If automatic detection fails, user can manually set in checklist.yaml:

```yaml
amex-platinum:
  anniversaryMonth: 11
  anniversaryDay: 15
```

### 2. Match Benefits

```
Matching transactions to benefits...

Amex Platinum:
  Jan 16: UBER EATS $18.50 → Uber Cash (January)
  Jan 18: LULULEMON $92.00 → Lululemon Q1 (over limit by $17)
  Jan 20: DISNEY PLUS $15.99 → Entertainment (January)

Chase Sapphire Reserve:
  Jan 17: LYFT $24.00 → Travel Credit
  Jan 19: AIRPORT PARKING $35.00 → Travel Credit
```

### 3. Identify Statement Credits

```
Finding statement credits...

Amex Platinum:
  Jan 17: UBER CASH CREDIT -$15.00 ✓
  Jan 19: LULULEMON CREDIT -$75.00 ✓
  Jan 21: ENTERTAINMENT CREDIT -$15.99 ✓

Chase Sapphire Reserve:
  Jan 18: TRAVEL CREDIT -$24.00 ✓
  Jan 20: TRAVEL CREDIT -$35.00 ✓
```

### 4. Update Checklist

```yaml
# Updates to checklist.yaml

amex-platinum:
  lastAnnualFeeDate: 2026-01-15
  benefits:
    uber-cash:
      monthsUsed: [1]  # January now tracked
    lululemon-q1:
      used: 75         # Credit amount, not spend amount
      transactions:
        - date: 2026-01-18
          amount: 92.00
          merchant: LULULEMON
          creditReceived: 75.00
          creditDate: 2026-01-19

config:
  sync:
    lastSyncDate: 2026-01-22
```

## Sync Summary

After sync completes, show summary:

```
Sync Complete
=============
Period: 2026-01-15 to 2026-01-22

Cards synced: 3
Transactions processed: 45
Benefit matches: 12
Credits received: 9

Benefits Updated:
─────────────────
Amex Platinum:
  • Uber Cash (Jan): ✓ Used ($15)
  • Lululemon Q1: $75 of $75 used
  • Entertainment (Jan): ✓ Used ($15.99)

Chase Sapphire Reserve:
  • Travel Credit: $59 of $300 used

Upcoming Expirations:
─────────────────────
  • Resy Q1 (Amex): $100 remaining - expires Mar 31
  • Saks H1 (Amex): $50 remaining - expires Jun 30

Next sync will fetch from: 2026-01-22
```

## Error Handling

### YNAB API Errors

```
Error: YNAB API returned 401 Unauthorized

Your YNAB token may have expired. To fix:
1. Go to https://app.ynab.com/settings/developer
2. Generate a new token
3. Update: ~/.config/credit-card-benefits/ynab-token
```

### Missing Account Mapping

```
Warning: No YNAB account mapped for 'delta-reserve'

To map this card:
1. Run /credit-card-benefits:configure
2. Or manually add to checklist.yaml:
   ynab.accountMapping.delta-reserve: "your-account-id"
```

### Sync Conflicts

```
Warning: Found transactions older than last sync date.

This can happen if:
- Transactions posted with earlier dates
- Manual edits to lastSyncDate

Recommendation: Run /credit-card-benefits:sync --full
```
