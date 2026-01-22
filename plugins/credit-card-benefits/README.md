# Credit Card Benefits Tracker Plugin

Track and maximize your premium credit card benefits with anniversary-aware checklists and optional YNAB integration.

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

## Commands

### `/credit-card-benefits:status [card] [--expiring] [--unused]`
Show status of all benefits and unused credits.

```bash
/credit-card-benefits:status              # All cards
/credit-card-benefits:status amex         # Just Amex Platinum
/credit-card-benefits:status --expiring   # Benefits expiring within 30 days
```

### `/credit-card-benefits:setup [card] [--open-date YYYY-MM-DD]`
Initialize tracking or configure card open dates.

```bash
/credit-card-benefits:setup                           # Interactive setup
/credit-card-benefits:setup venture-x --open-date 2023-06-15
```

### `/credit-card-benefits:use <card> <benefit> [amount]`
Record using a benefit.

```bash
/credit-card-benefits:use amex lululemon              # Full credit used
/credit-card-benefits:use amex resy 75 --notes "Carbone dinner"
/credit-card-benefits:use chase travel 150
```

### `/credit-card-benefits:info <card>`
Show detailed benefit information for a card.

```bash
/credit-card-benefits:info amex
/credit-card-benefits:info chase
```

### `/credit-card-benefits:remind [days]`
Show benefits expiring soon that need attention.

```bash
/credit-card-benefits:remind          # Next 30 days
/credit-card-benefits:remind 7        # Next 7 days
```

### `/credit-card-benefits:ynab [analyze|credits|match]`
Analyze YNAB transactions to find and match credit card credits.

```bash
/credit-card-benefits:ynab setup      # Configure YNAB integration
/credit-card-benefits:ynab analyze    # Analyze transactions
/credit-card-benefits:ynab credits    # Find statement credits
```

## Agent

The `benefits-tracker` agent can be invoked naturally:

- "What Amex credits do I still need to use?"
- "Show me my unused Chase Sapphire benefits"
- "What benefits are expiring this month?"
- "I just used my Lululemon credit"

## Data Storage

Your tracking data is stored at:
```
~/.config/credit-card-benefits/checklist.json
```

## Key Features

### Reset Type Awareness

The plugin understands different reset types:

- **Calendar Year**: Resets January 1 (most Amex/Chase credits)
- **Account Anniversary**: Resets on your card open date (Venture X, Alaska)
- **Monthly**: Must be used each month (Uber Cash, Entertainment)
- **Quarterly**: Four periods per year (Resy, Lululemon)
- **Semi-annual**: Two periods (Hotels, Saks)

### 2026 Special Features

- **Chase Select Hotels Credit**: One-time $250 credit for IHG, Montage, Pendry, Omni, Virgin, Minor, Pan Pacific hotels
- **Credit Stacking**: Combine up to $800 on one Chase hotel stay (Edit + Select + Travel)
- **Venture X Lounge Changes**: Guest fees starting Feb 2026

### YNAB Integration

Connect to YNAB to:
- Automatically detect transactions matching benefit patterns
- Find statement credits and match to benefits
- Identify unused monthly credits
- Verify credits were received

## Quick Reference: Benefits by Reset Period

### Monthly (Use Every Month)
- Amex: Uber Cash ($15), Entertainment ($25), Equinox ($25)
- Delta: Resy ($20), Rideshare ($10)

### Quarterly (4x/year)
- Amex: Resy ($100), Lululemon ($75)

### Semi-Annual (2x/year)
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
