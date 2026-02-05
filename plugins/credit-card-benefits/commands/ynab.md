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
2. Fetches your YNAB budgets and accounts
3. Maps each credit card to its YNAB account
4. Saves configuration to checklist.yaml

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

## Setup Execution Steps

When `/credit-card-benefits:ynab setup` runs, follow these steps:

### Step 1: Check Existing Token

```bash
# Check macOS Keychain for existing token
KEYCHAIN_SERVICE="env/YNAB_API_TOKEN"
TOKEN=$(security find-generic-password -s "$KEYCHAIN_SERVICE" -w 2>/dev/null)

if [ -n "$TOKEN" ]; then
  echo "Existing YNAB token found in Keychain"
fi

# Migration: Check for legacy file-based token and migrate to Keychain
LEGACY_TOKEN_FILE="$HOME/.config/credit-card-benefits/ynab-token"
if [ -z "$TOKEN" ] && [ -f "$LEGACY_TOKEN_FILE" ]; then
  echo "Found legacy token file - migrating to Keychain..."
  LEGACY_TOKEN=$(cat "$LEGACY_TOKEN_FILE")

  # Try to add to keychain (delete first if exists, then add)
  security delete-generic-password -s "$KEYCHAIN_SERVICE" 2>/dev/null
  security add-generic-password -s "$KEYCHAIN_SERVICE" -a "$USER" -w "$LEGACY_TOKEN"

  # Verify migration succeeded before deleting legacy file
  VERIFY_TOKEN=$(security find-generic-password -s "$KEYCHAIN_SERVICE" -w 2>/dev/null)
  if [ "$VERIFY_TOKEN" = "$LEGACY_TOKEN" ]; then
    rm "$LEGACY_TOKEN_FILE"
    echo "✓ Token migrated to Keychain, legacy file removed"
    TOKEN="$LEGACY_TOKEN"
  else
    echo "ERROR: Failed to migrate token to Keychain. Legacy file preserved."
    echo "You may need to unlock your keychain or check permissions."
    TOKEN="$LEGACY_TOKEN"  # Use the legacy token for this session
  fi
fi
```

If token exists, use AskUserQuestion:
```yaml
question: "An existing YNAB token was found. What would you like to do?"
header: "Token"
options:
  - label: "Use existing token"
    description: "Validate and continue with the saved token"
  - label: "Enter new token"
    description: "Replace with a new YNAB Personal Access Token"
  - label: "Cancel"
    description: "Keep current settings and exit"
```

### Step 2: Get New Token (if needed)

Display instructions:
```
To connect YNAB, you'll need a Personal Access Token:

1. Go to: https://app.ynab.com/settings/developer
2. Click "New Token"
3. Give it a name like "Credit Card Benefits"
4. Copy the token (you won't see it again!)
```

Use AskUserQuestion:
```yaml
question: "Are you ready to enter your YNAB token?"
header: "Token"
options:
  - label: "Yes, I have my token"
    description: "I've copied my YNAB Personal Access Token"
  - label: "Open YNAB settings first"
    description: "Open https://app.ynab.com/settings/developer in my browser"
  - label: "Cancel"
    description: "I'll do this later"
```

If "Open YNAB settings first":
```bash
open "https://app.ynab.com/settings/developer"
```
Then repeat the question.

If "Yes, I have my token", prompt user to paste it, then store in macOS Keychain:
```bash
KEYCHAIN_SERVICE="env/YNAB_API_TOKEN"

# Delete existing entry if present, then add new one
security delete-generic-password -s "$KEYCHAIN_SERVICE" 2>/dev/null
security add-generic-password -s "$KEYCHAIN_SERVICE" -a "$USER" -w "$USER_TOKEN"

# Verify token was stored successfully
VERIFY_TOKEN=$(security find-generic-password -s "$KEYCHAIN_SERVICE" -w 2>/dev/null)
if [ "$VERIFY_TOKEN" = "$USER_TOKEN" ]; then
  echo "✓ Token saved securely to macOS Keychain"
else
  echo "ERROR: Failed to save token to Keychain. Check keychain permissions."
  exit 1
fi
```

### Step 3: Validate Token and Fetch Budgets

```bash
KEYCHAIN_SERVICE="env/YNAB_API_TOKEN"

# Only fetch from Keychain if not already set (e.g., from migration fallback)
if [ -z "$TOKEN" ]; then
  TOKEN=$(security find-generic-password -s "$KEYCHAIN_SERVICE" -w 2>/dev/null)
fi

if [ -z "$TOKEN" ]; then
  echo "ERROR: No YNAB token found in Keychain"
  echo "Run setup again to add your token"
  exit 1
fi

# Test token by fetching budgets
RESPONSE=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" \
  "https://api.youneedabudget.com/v1/budgets")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "401" ]; then
  echo "ERROR: Invalid token (HTTP 401)"
  exit 1
elif [ "$HTTP_CODE" != "200" ]; then
  echo "ERROR: API request failed (HTTP $HTTP_CODE)"
  exit 1
fi

# List budgets
echo "$BODY" | jq -r '.data.budgets[] | "• \(.name) (ID: \(.id[0:8])...)"'
```

**Error handling:**

If HTTP 401:
```
Error: YNAB returned 401 Unauthorized

Your token appears to be invalid or expired. Please:
1. Go to https://app.ynab.com/settings/developer
2. Delete the old token if it exists
3. Generate a new token
4. Run /credit-card-benefits:ynab setup again
```

If HTTP 500 or network error:
```
Error: Could not connect to YNAB API

Please check your internet connection. If the problem persists,
YNAB's API may be temporarily unavailable. Try again in a few minutes.
```

### Step 4: Select Budget

Build AskUserQuestion options dynamically from the budgets list:

```yaml
question: "Which budget contains your credit card accounts?"
header: "Budget"
options:
  # Built from API response:
  - label: "My Budget"
    description: "ID: abc123-de... | Last modified: 2026-01-20"
  - label: "Business Budget"
    description: "ID: xyz789-ab... | Last modified: 2026-01-15"
```

Store the selected budget ID:
```bash
BUDGET_ID="<selected-budget-id>"
```

### Step 5: Fetch Credit Card Accounts

```bash
ACCOUNTS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.youneedabudget.com/v1/budgets/$BUDGET_ID/accounts")

# Filter to credit cards only and format output
echo "$ACCOUNTS_RESPONSE" | jq -r '
  .data.accounts[]
  | select(.type == "creditCard" and .closed == false)
  | "• \(.name) | Balance: $\(.balance / 1000 | fabs | . * 100 | floor / 100)"'
```

If no credit card accounts:
```
Warning: No credit card accounts found in this budget.

Your credit cards need to be set up as "Credit Card" type accounts in YNAB.
Would you like to:
1. Select a different budget
2. Continue without YNAB mapping (manual tracking only)
3. Cancel setup
```

### Step 6: Map Accounts to Cards

For each premium credit card, use AskUserQuestion to map.

First, build the YNAB accounts list for options:
```bash
# Get account options
ACCOUNT_OPTIONS=$(echo "$ACCOUNTS_RESPONSE" | jq -r '
  .data.accounts[]
  | select(.type == "creditCard" and .closed == false)
  | "\(.name)|\(.id)|\(.balance)"')
```

Then for each card (amex-platinum, chase-sapphire-reserve, capital-one-venture-x, delta-reserve, alaska-atmos-summit):

```yaml
question: "Which YNAB account is your American Express Platinum?"
header: "Amex"
options:
  # Built from YNAB accounts:
  - label: "Amex Platinum"
    description: "Balance: -$1,250.00 | ID: 111aaa..."
  - label: "Chase Freedom"
    description: "Balance: -$89.50 | ID: 222bbb..."
  # ... other YNAB credit card accounts
  - label: "I don't have this card"
    description: "Skip - don't track American Express Platinum"
```

Repeat for each premium card type.

### Step 7: Save Configuration

Read existing checklist or create from template:
```bash
CONFIG_FILE="$HOME/.claude/data/credit-card-benefits/checklist.yaml"
TEMPLATE_FILE="<plugin-path>/data/checklist-template.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
  cp "$TEMPLATE_FILE" "$CONFIG_FILE"
fi
```

Update the config section in checklist.yaml:

```yaml
config:
  setupComplete: true
  setupDate: "2026-01-24"

  dataSource:
    primary: ynab-api

    ynab:
      method: api
      budgetId: "abc123-def456-ghi789-..."
      accountMapping:
        amex-platinum: "111-aaa-bbb-ccc-..."
        chase-sapphire-reserve: "222-ddd-eee-fff-..."
        capital-one-venture-x: null
        alaska-atmos-summit: null
        delta-reserve: "333-ggg-hhh-iii-..."

    csv:
      importDirectory: ~/Downloads

  cards:
    enabled:
      - amex-platinum
      - chase-sapphire-reserve
      - delta-reserve
    disabled:
      - capital-one-venture-x
      - alaska-atmos-summit

  sync:
    initialSyncDate: null
    lastSyncDate: null
    autoSync: false
```

### Step 8: Confirmation

```
✓ YNAB setup complete!

Configuration saved:
• Budget: "My Budget"
• Mapped accounts:
  - Amex Platinum → "Amex Platinum" (111aaa...)
  - Chase Sapphire Reserve → "Chase Sapphire" (222bbb...)
  - Delta Reserve → "Delta SkyMiles" (333ccc...)

Not mapped (will use manual tracking):
  - Capital One Venture X
  - Alaska Atmos Summit

Next: Run /credit-card-benefits:sync to pull transactions and detect benefit usage.
```

---

## Security Notes

- **Token storage**: macOS Keychain
  - Service name: `env/YNAB_API_TOKEN`
  - Encrypted by macOS at rest
  - Protected by your login password
  - Never stored in plain text files
  - Never displayed in output

- **Data processing**: All transaction analysis happens locally

- **Stored data**: Only IDs and timestamps saved to checklist.yaml
  - No transaction amounts or descriptions persisted
  - No sensitive financial data in config

- **Migration**: Legacy tokens in `~/.claude/data/credit-card-benefits/ynab-token` are automatically migrated to Keychain and the file is deleted

---

## API Reference

### Base URL
```
https://api.youneedabudget.com/v1
```

### Authentication
```bash
curl -H "Authorization: Bearer $(security find-generic-password -s 'env/YNAB_API_TOKEN' -w)" <url>
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

1. **Token Storage**: macOS Keychain (service: `env/YNAB_API_TOKEN`)
   - Encrypted at rest by macOS
   - Protected by login keychain password
   - Never stored in plain text files
   - Never displayed in logs or output

2. **Data Processing**: All transaction analysis happens locally

3. **Stored Data**: Only account IDs and sync timestamps are saved to checklist.yaml
   - No transaction data is persisted
   - No sensitive financial amounts stored
