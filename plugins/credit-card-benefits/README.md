# Credit Card Benefits Tracker Plugin

Track and maximize your premium credit card benefits with anniversary-aware checklists, multiple data source support, and automatic transaction matching.

## Supported Cards

| Card | Annual Fee | Reset Type |
|------|------------|------------|
| American Express Platinum | $895 | Calendar Year / Monthly |
| Capital One Venture X | $395 | Account Anniversary |
| Chase Sapphire Reserve | $795 | Mixed (Anniversary + Calendar) |
| Bank of America Alaska Airlines Atmos Summit | $395 | Account Anniversary |
| Delta SkyMiles Reserve | $650 | Mixed (Monthly + Anniversary) |

## Installation

```bash
/plugin install credit-card-benefits@omarshahine-agent-plugins
```

## Quick Start

```bash
# 1. Configure your cards and data source
/credit-card-benefits:configure

# 2. Initial sync pulls 12 months of history to find anniversaries
/credit-card-benefits:sync --full

# 3. Check your benefit status
/credit-card-benefits:status

# 4. Set up reminders for expiring credits
/credit-card-benefits:remind
```

## Data Sources

The plugin supports multiple ways to track your transactions:

| Source | Best For | Setup |
|--------|----------|-------|
| **YNAB MCP** | YNAB users with MCP server | Auto-detected |
| **YNAB API** | YNAB users | Requires API token |
| **CSV Import** | Any card | Download from card website |
| **Manual** | Simple tracking | No external data |

## Commands

### `/credit-card-benefits:configure`
**Start here!** Interactive setup for cards and data sources.

```bash
/credit-card-benefits:configure
```

### `/credit-card-benefits:sync [--full] [--since DATE]`
Sync transactions from your configured data source.

```bash
/credit-card-benefits:sync           # Incremental (since last sync)
/credit-card-benefits:sync --full    # Full 12-month resync
```

### `/credit-card-benefits:status [card] [--expiring]`
Show status of all benefits and unused credits.

```bash
/credit-card-benefits:status              # All cards
/credit-card-benefits:status amex         # Just Amex Platinum
/credit-card-benefits:status --expiring   # Benefits expiring soon
```

### `/credit-card-benefits:import <file.csv> [--card name]`
Import transactions from CSV files.

```bash
/credit-card-benefits:import ~/Downloads/amex-jan.csv --card amex-platinum
/credit-card-benefits:import statement.csv --format chase
```

Supported formats: Amex, Chase, Capital One, YNAB export, generic CSV

### `/credit-card-benefits:remind [days]`
Show benefits expiring soon that need attention.

```bash
/credit-card-benefits:remind          # Next 30 days
/credit-card-benefits:remind 7        # Next 7 days (urgent)
```

### `/credit-card-benefits:use <card> <benefit> [amount]`
Manually record using a benefit.

```bash
/credit-card-benefits:use amex lululemon
/credit-card-benefits:use amex resy 75 --notes "Carbone dinner"
```

### `/credit-card-benefits:info <card>`
Show detailed benefit information for a card.

```bash
/credit-card-benefits:info amex
/credit-card-benefits:info chase
```

### `/credit-card-benefits:update [card] [--all] [--dry-run]`
Research current benefits online and update your checklist with changes.

```bash
/credit-card-benefits:update amex-platinum    # Update one card
/credit-card-benefits:update --all            # Update all cards
/credit-card-benefits:update --dry-run        # Preview changes only
```

The update command:
1. Searches official card issuer sites and trusted sources (TPG, NerdWallet)
2. Compares found benefits against your current checklist
3. Asks for approval before adding new benefits or removing old ones
4. Logs all changes to `updateHistory` in your checklist

**Recommended frequency:** Monthly during Q1, quarterly otherwise, or after major card announcements.

## Agent

The `benefits-tracker` agent can be invoked naturally:

- "What Amex credits do I still need to use?"
- "Show me my unused Chase Sapphire benefits"
- "What benefits are expiring this month?"
- "I just used my Lululemon credit"
- "Import my latest Amex statement"

## Data Storage

```
~/.config/credit-card-benefits/
├── checklist.yaml      # Main tracking data (YAML for easy editing)
└── ynab-token          # YNAB API token (if using YNAB API)
```

## How Anniversary Detection Works

The plugin uses **annual fee posting date** as the most reliable anniversary indicator:

1. During initial sync, it looks back 12 months for annual fee transactions
2. Patterns detected: "ANNUAL FEE", "ANNUAL MEMBERSHIP FEE", etc.
3. The posting date becomes your `lastAnnualFeeDate`
4. `nextAnnualFeeDate` is calculated automatically

This is more reliable than card open date because:
- Anniversary benefits reset when the fee posts, not when you applied
- Fee posting dates can shift slightly year to year
- The plugin tracks `annualFeeHistory` for reference

## Key Features

### Reset Type Awareness

| Type | When It Resets | Examples |
|------|----------------|----------|
| Calendar Year | January 1 | Amex Resy, Lululemon, Airline |
| Anniversary | Annual fee date | Venture X Travel, Alaska Passes |
| Monthly | 1st of month | Uber Cash, Entertainment |
| Quarterly | Q1-Q4 boundaries | Amex Resy, Lululemon |
| Semi-annual | Jan 1 / Jul 1 | Amex Hotel, Saks, Chase Edit |

### 2026 Special Features

- **Chase Select Hotels Credit**: One-time $250 for IHG, Montage, Pendry, Omni, Virgin, Minor, Pan Pacific
- **Credit Stacking**: Combine up to $800 on one Chase hotel stay
- **Venture X Lounge Changes**: Guest fees starting Feb 2026

### Incremental Sync

After initial setup:
- Sync only fetches transactions since `lastSyncDate`
- Faster and more efficient
- Run `/credit-card-benefits:sync` weekly or monthly

## Quick Reference: Benefits by Reset Period

### Monthly (Use Every Month!)
- Amex: Uber Cash ($15), Entertainment ($25), Equinox ($25)
- Delta: Resy ($20), Rideshare ($10)

### Quarterly
- Amex: Resy ($100), Lululemon ($75)

### Semi-Annual
- Amex: Hotel ($300), Saks ($50)
- Chase: The Edit ($250), Exclusive Tables ($150)

### Annual
- Amex: Airline Fee ($200), CLEAR ($209)
- Venture X: Travel ($300), 10K Miles
- Chase: Travel ($300)
- Delta: Delta Stays ($200), Companion Cert
- Alaska: 8 Lounge Passes, Companion Fare

## Sources

Benefits research sourced from:
- [American Express](https://www.americanexpress.com/)
- [Capital One](https://www.capitalone.com/)
- [Chase](https://www.chase.com/)
- [Bank of America](https://www.bankofamerica.com/)
- [Delta Air Lines](https://www.delta.com/)
- [The Points Guy](https://thepointsguy.com/)
- [NerdWallet](https://www.nerdwallet.com/)

*Last updated: January 2026*
