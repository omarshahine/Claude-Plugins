---
description: Configure data sources and initial setup for credit card benefits tracking
argument-hint: "[--reconfigure]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - AskUserQuestion
---

# Configure Credit Card Benefits Tracker

Interactive setup to configure your data source and credit cards for benefits tracking.

## Execution Steps

When this command runs, follow these steps in order:

### Step 1: Check for Existing Configuration

```bash
# Check if config file exists
CONFIG_DIR="$HOME/.config/credit-card-benefits"
CONFIG_FILE="$CONFIG_DIR/checklist.yaml"

if [ -f "$CONFIG_FILE" ]; then
  echo "Existing configuration found"
fi
```

If config exists, use AskUserQuestion:
```
Your credit card benefits are already configured.

Options:
1. View current settings
2. Reconfigure from scratch
3. Update card selection only
4. Cancel
```

### Step 2: Select Data Source

Use AskUserQuestion with these options:

```yaml
question: "Which data source would you like to use for transaction tracking?"
header: "Data source"
options:
  - label: "YNAB (Recommended)"
    description: "Connect to You Need A Budget for automatic transaction matching. Best if you already use YNAB."
  - label: "CSV Import"
    description: "Download statement CSVs from card websites and import them. Works with any card."
  - label: "Manual"
    description: "Track benefits manually without transaction data. Simple but requires more effort."
```

### Step 3: YNAB Setup (if selected)

#### 3a. Display Token Instructions

Show this message:
```
To connect to YNAB, you'll need a Personal Access Token:

1. Open: https://app.ynab.com/settings/developer
2. Click "New Token"
3. Name it "Credit Card Benefits"
4. Copy the token (you won't see it again!)

Once you have the token, paste it below.
```

Then use AskUserQuestion:
```yaml
question: "Paste your YNAB API token:"
header: "Token"
options:
  - label: "I have my token ready"
    description: "I've copied my YNAB Personal Access Token and am ready to paste it"
  - label: "Open YNAB settings"
    description: "Open https://app.ynab.com/settings/developer in browser first"
  - label: "Cancel setup"
    description: "I'll set this up later"
```

If user selects "I have my token ready", prompt them to enter the token. Store it securely:

```bash
mkdir -p ~/.config/credit-card-benefits
# User provides token
echo "$TOKEN" > ~/.config/credit-card-benefits/ynab-token
chmod 600 ~/.config/credit-card-benefits/ynab-token
```

#### 3b. Validate Token and Fetch Budgets

```bash
TOKEN=$(cat ~/.config/credit-card-benefits/ynab-token)

# Validate token by fetching budgets
RESPONSE=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" \
  "https://api.youneedabudget.com/v1/budgets")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo "Error: YNAB returned HTTP $HTTP_CODE"
  echo "Your token appears to be invalid. Please generate a new one."
  exit 1
fi

# Extract budget names and IDs
echo "$BODY" | jq -r '.data.budgets[] | "\(.name) (\(.id))"'
```

If token is invalid, show error:
```
Error: YNAB returned 401 Unauthorized

Your token appears to be invalid. Please:
1. Go to https://app.ynab.com/settings/developer
2. Generate a new token
3. Run /credit-card-benefits:configure again
```

#### 3c. Select Budget

Use AskUserQuestion with the fetched budgets as options. Build options dynamically from API response.

Example with 2 budgets:
```yaml
question: "Which budget contains your credit card accounts?"
header: "Budget"
options:
  - label: "My Budget"
    description: "Budget ID: abc123-def456-..."
  - label: "Business Budget"
    description: "Budget ID: ghi789-jkl012-..."
```

#### 3d. Fetch Credit Card Accounts

```bash
BUDGET_ID="<selected-budget-id>"

curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.youneedabudget.com/v1/budgets/$BUDGET_ID/accounts" \
  | jq -r '.data.accounts[] | select(.type == "creditCard") | "\(.name) | \(.id) | Balance: \(.balance / 1000)"'
```

If no credit card accounts found:
```
Warning: No credit card accounts found in budget "My Budget"

Make sure your credit cards are set up as "Credit Card" type accounts in YNAB.
You can still continue with manual tracking or add accounts later.
```

#### 3e. Map Accounts to Cards

For each premium card, use AskUserQuestion to map it to a YNAB account.

Example for Amex Platinum:
```yaml
question: "Which YNAB account is your American Express Platinum?"
header: "Amex Platinum"
options:
  - label: "Amex Platinum"
    description: "YNAB account: 111-aaa-... (Balance: -$1,250.00)"
  - label: "Chase Sapphire Reserve"
    description: "YNAB account: 222-bbb-... (Balance: -$500.00)"
  - label: "Capital One Venture X"
    description: "YNAB account: 333-ccc-... (Balance: -$890.00)"
  - label: "I don't have this card"
    description: "Skip - I don't have an American Express Platinum"
```

Repeat for each card: Chase Sapphire Reserve, Capital One Venture X, Delta Reserve, Alaska Atmos.

### Step 4: CSV Setup (if selected)

Show CSV instructions:
```
CSV Import Setup
================

You'll download statement CSVs from each credit card website:

• Amex: amex.com → Account → Statements & Activity → Download CSV
• Chase: chase.com → See Activity → Download account activity
• Capital One: capitalone.com → Account → Download Transactions
• Bank of America: bankofamerica.com → Activity → Download

Files will be auto-detected from their headers.
```

Use AskUserQuestion for import directory:
```yaml
question: "Where should I look for downloaded CSV files?"
header: "CSV folder"
options:
  - label: "~/Downloads (Recommended)"
    description: "Default browser download location - easiest option"
  - label: "~/Documents/Statements"
    description: "Dedicated folder for financial statements"
  - label: "Custom location"
    description: "Specify a different folder path"
```

### Step 5: Select Cards to Track

Use AskUserQuestion with multiSelect:
```yaml
question: "Which premium credit cards do you have?"
header: "Your cards"
multiSelect: true
options:
  - label: "American Express Platinum ($895/year)"
    description: "Uber, Saks, airline credits, Centurion lounges, hotel credits, and more"
  - label: "Chase Sapphire Reserve ($795/year)"
    description: "Travel credit, DoorDash, Lyft, Priority Pass lounges, The Edit hotel credits"
  - label: "Capital One Venture X ($395/year)"
    description: "Travel credit, Capital One lounges, anniversary miles bonus"
  - label: "Delta SkyMiles Reserve ($650/year)"
    description: "Sky Club access, companion certificate, Resy credit, rideshare credit"
  - label: "Alaska Atmos Summit ($395/year)"
    description: "Lounge passes, companion fare, free bags, Wi-Fi passes"
```

### Step 6: Save Configuration

Create the config directory and save the checklist:

```bash
mkdir -p ~/.config/credit-card-benefits
```

Write configuration to `~/.config/credit-card-benefits/checklist.yaml`:

```yaml
# Credit Card Benefits Configuration
# Generated by /credit-card-benefits:configure

config:
  setupComplete: true
  setupDate: "2026-01-24"

  dataSource:
    primary: ynab-api  # or: csv, manual

    ynab:
      method: api
      budgetId: "abc123-def456-..."
      accountMapping:
        amex-platinum: "111-aaa-..."      # or null if not mapped
        chase-sapphire-reserve: "222-bbb-..."
        capital-one-venture-x: null
        alaska-atmos-summit: null
        delta-reserve: "333-ccc-..."

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

### Step 7: Confirmation & Next Steps

Show completion message:
```
✓ Configuration saved to ~/.config/credit-card-benefits/checklist.yaml

Your setup:
• Data source: YNAB API
• Budget: "My Budget"
• Cards tracked: Amex Platinum, Chase Sapphire Reserve, Delta Reserve

Next steps:
• /credit-card-benefits:sync - Run first to detect card anniversary dates from annual fee transactions
• /credit-card-benefits:status - View your current benefits
• /credit-card-benefits:remind - See benefits expiring soon

Note: Card anniversary dates will be automatically detected from annual fee
transactions when you run sync. This is needed for cardmember-year benefits.
```

---

## Error Handling

### Invalid YNAB Token
```
Error: YNAB returned 401 Unauthorized

Your token appears to be invalid. Please:
1. Go to https://app.ynab.com/settings/developer
2. Generate a new token
3. Run /credit-card-benefits:configure again
```

### No Credit Card Accounts Found
```
Warning: No credit card accounts found in budget "My Budget"

This could mean:
• Your credit cards aren't set up as "Credit Card" type in YNAB
• The cards are in a different budget

You can continue setup and map accounts later, or fix this in YNAB first.
```

### Network Error
```
Error: Could not connect to YNAB API

Please check your internet connection and try again.
If the problem persists, YNAB's API may be temporarily unavailable.
```

---

## File Locations

| File | Purpose |
|------|---------|
| `~/.config/credit-card-benefits/checklist.yaml` | Main configuration and benefit tracking |
| `~/.config/credit-card-benefits/ynab-token` | YNAB API token (chmod 600) |

---

## Post-Setup

After configuration:
- `/credit-card-benefits:status` - See all benefits and usage
- `/credit-card-benefits:sync` - Pull new transactions from YNAB/CSV
- `/credit-card-benefits:remind` - Get alerts for expiring benefits
- `/credit-card-benefits:configure --reconfigure` - Start over
