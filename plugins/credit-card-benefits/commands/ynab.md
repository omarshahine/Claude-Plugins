---
description: Connect to YNAB for transaction analysis and automatic benefit matching
argument-hint: "[setup|analyze|credits|match] [--since YYYY-MM-DD]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
  - AskUserQuestion
---

# YNAB Integration

Connect to YNAB (You Need A Budget) to automatically analyze credit card transactions and match them to your benefits.

## Commands

### Setup (First Time)

```
/credit-card-benefits:ynab setup
```

Interactive setup that:
1. Prompts for your YNAB API token (stored securely)
2. Fetches your YNAB accounts
3. Maps each credit card to its YNAB account

### Analyze Transactions

```
/credit-card-benefits:ynab analyze [--since YYYY-MM-DD]
```

Fetch and analyze transactions to find benefit usage and statement credits.

### Find Credits

```
/credit-card-benefits:ynab credits
```

List all statement credits received on your cards.

### Match & Update

```
/credit-card-benefits:ynab match
```

Interactively match transactions to benefits and update your checklist.

---

## Setup Flow

### Step 1: Get YNAB API Token

Direct the user to get their token:

```
To connect YNAB, you'll need a Personal Access Token:

1. Go to: https://app.ynab.com/settings/developer
2. Click "New Token"
3. Give it a name like "Credit Card Benefits"
4. Copy the token (you won't see it again!)
```

### Step 2: Store Token Securely

The token is stored at `~/.config/credit-card-benefits/ynab-token`

```bash
# Create config directory (not in git)
mkdir -p ~/.config/credit-card-benefits

# Store the token (user provides it)
echo "YOUR_TOKEN_HERE" > ~/.config/credit-card-benefits/ynab-token
chmod 600 ~/.config/credit-card-benefits/ynab-token
```

**Security notes:**
- Token file is in user's home config, NOT in the plugin/git
- File permissions set to 600 (owner read/write only)
- Never log or display the full token

### Step 3: Fetch YNAB Accounts

Use the YNAB API to list accounts:

```bash
TOKEN=$(cat ~/.config/credit-card-benefits/ynab-token)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.youneedabudget.com/v1/budgets/last-used/accounts" | jq
```

Response includes:
```json
{
  "data": {
    "accounts": [
      {
        "id": "12345678-abcd-...",
        "name": "Amex Platinum",
        "type": "creditCard",
        "balance": -125000
      },
      {
        "id": "87654321-dcba-...",
        "name": "Chase Sapphire Reserve",
        "type": "creditCard",
        "balance": -50000
      }
    ]
  }
}
```

### Step 4: Map Accounts

Present the credit card accounts to the user and ask them to map:

```
Found these credit card accounts in YNAB:

1. Amex Platinum (id: 12345678-abcd-...)
2. Chase Sapphire Reserve (id: 87654321-dcba-...)
3. Capital One Venture X (id: ...)

Which YNAB account corresponds to each card?

Amex Platinum → [1] Amex Platinum
Capital One Venture X → [3] Capital One Venture X
Chase Sapphire Reserve → [2] Chase Sapphire Reserve
Alaska Atmos → [none]
Delta Reserve → [none]
```

### Step 5: Save Configuration

Update the checklist.yaml with the account mapping:

```yaml
ynab:
  enabled: true
  budgetId: "budget-uuid-here"
  lastSync: null
  accountMapping:
    amex-platinum: "12345678-abcd-..."
    capital-one-venture-x: "..."
    chase-sapphire-reserve: "87654321-dcba-..."
    alaska-atmos-summit: null
    delta-reserve: null
```

---

## API Reference

### Base URL
```
https://api.youneedabudget.com/v1
```

### Authentication
```bash
curl -H "Authorization: Bearer $(cat ~/.config/credit-card-benefits/ynab-token)" <url>
```

### Useful Endpoints

**List Budgets:**
```
GET /budgets
```

**List Accounts:**
```
GET /budgets/{budget_id}/accounts
```

**Get Transactions:**
```
GET /budgets/{budget_id}/accounts/{account_id}/transactions?since_date=2026-01-01
```

---

## Transaction Matching Patterns

### Benefit Purchases

| Card | Benefit | Merchant Patterns |
|------|---------|-------------------|
| Amex Platinum | Uber Cash | UBER, UBER EATS |
| Amex Platinum | Lululemon | LULULEMON |
| Amex Platinum | Saks | SAKS, SAKSFIFTHAVENUE |
| Amex Platinum | Entertainment | DISNEY, HULU, ESPN, PEACOCK, PARAMOUNT, NYT, WSJ, YOUTUBE |
| Amex Platinum | Equinox | EQUINOX |
| Amex Platinum | Resy | Restaurants booked via Resy |
| Delta Reserve | Resy | Restaurants booked via Resy |
| Delta Reserve | Rideshare | LYFT, UBER (rides only) |
| Venture X | Travel | CAPITAL ONE TRAVEL |
| Sapphire Reserve | Travel | CHASE TRAVEL, airlines, hotels, Uber, Lyft, parking |

### Statement Credits

Look for negative amounts (inflows in YNAB) with patterns:
- `STATEMENT CREDIT`
- `UBER CASH CREDIT`
- `ENTERTAINMENT CREDIT`
- `SAPPHIRE RESERVE CREDIT`
- `TRAVEL CREDIT`

### Annual Fees

Detect annual fee postings to auto-set anniversary dates:
- `ANNUAL FEE`
- `ANNUAL MEMBERSHIP FEE`
- `YEARLY MEMBERSHIP`
- Amount matches known fees: $895, $795, $650, $395

---

## Output Examples

### Analyze Output

```
YNAB Transaction Analysis
========================
Period: 2026-01-01 to 2026-01-22

AMEX PLATINUM
─────────────
Benefit Matches:
  ✓ Jan 5: UBER EATS $18.50 → Uber Cash (Jan)
  ✓ Jan 8: LULULEMON $89.00 → Lululemon Q1 (partial: $75 credited)
  ✓ Jan 12: DISNEY PLUS $15.99 → Entertainment (Jan)

Credits Received:
  ✓ Jan 6: UBER CASH CREDIT $15.00
  ✓ Jan 9: LULULEMON CREDIT $75.00
  ✓ Jan 13: ENTERTAINMENT CREDIT $15.99

CHASE SAPPHIRE RESERVE
──────────────────────
Benefit Matches:
  ✓ Jan 10: LYFT $25.00 → Travel Credit
  ✓ Jan 15: PARKING $12.00 → Travel Credit

Credits Received:
  ✓ Jan 11: SAPPHIRE TRAVEL CREDIT $25.00
  ✓ Jan 16: SAPPHIRE TRAVEL CREDIT $12.00

ANNUAL FEE DETECTED
───────────────────
  Jan 15: AMEX PLATINUM ANNUAL FEE $895.00
  → Updated anniversary date to January 15
```

---

## Security & Privacy

1. **Token Storage**: `~/.config/credit-card-benefits/ynab-token`
   - Outside of any git repository
   - File permissions: 600 (owner only)
   - Never displayed in logs or output

2. **Data Processing**: All transaction analysis happens locally

3. **Stored Data**: Only account IDs and sync timestamps are saved to checklist.yaml
   - No transaction data is persisted
   - No sensitive financial amounts stored
