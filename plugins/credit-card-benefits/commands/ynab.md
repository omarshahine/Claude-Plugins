---
description: Analyze YNAB transactions to find credit card credits and match to benefits
argument-hint: "[analyze|credits|match] [--account name] [--since YYYY-MM-DD]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
---

# YNAB Credit Card Benefits Analysis

Integrate with YNAB to analyze credit card transactions and identify used/unused benefits.

## Prerequisites

1. **YNAB API Token**: User must have a YNAB API token stored at `~/.config/credit-card-benefits/ynab-token`
2. **Account Mapping**: Map YNAB accounts to credit cards in the checklist

## Setup

If no YNAB token is configured, instruct the user:

```
To use YNAB integration:
1. Go to https://app.ynab.com/settings/developer
2. Create a new Personal Access Token
3. Save it to ~/.config/credit-card-benefits/ynab-token
4. Run /credit-card-benefits:ynab setup to configure account mapping
```

## Operations

### Setup Account Mapping

```
/credit-card-benefits:ynab setup
```

This will:
1. Fetch YNAB accounts via API
2. Let user map each credit card to a YNAB account
3. Save mapping to checklist.json

### Analyze Transactions

```
/credit-card-benefits:ynab analyze [--since YYYY-MM-DD]
```

This will:
1. Fetch transactions from mapped credit card accounts
2. Look for transactions matching benefit patterns
3. Look for statement credits
4. Generate a report of potential benefit usage

### Find Statement Credits

```
/credit-card-benefits:ynab credits [--account name]
```

Find all statement credits (negative transactions) on credit card accounts and categorize them by likely source.

### Match and Update

```
/credit-card-benefits:ynab match
```

Interactively match transactions to benefits and update the checklist.

## YNAB API Usage

### Base URL
```
https://api.youneedabudget.com/v1
```

### Authentication
```bash
curl -H "Authorization: Bearer ${YNAB_TOKEN}" https://api.youneedabudget.com/v1/budgets
```

### Get Transactions
```bash
curl -H "Authorization: Bearer ${YNAB_TOKEN}" \
  "https://api.youneedabudget.com/v1/budgets/last-used/accounts/{account_id}/transactions?since_date=2025-01-01"
```

## Transaction Matching Patterns

### Amex Platinum
| Benefit | Payee Patterns | Category Hints |
|---------|----------------|----------------|
| Uber | UBER, UBER EATS, UBEREATS | Transportation, Food |
| Resy | Various restaurants | Restaurants |
| Lululemon | LULULEMON | Shopping |
| Saks | SAKS, SAKSFIFTHAVENUE | Shopping |
| Entertainment | DISNEY, HULU, ESPN, PEACOCK, PARAMOUNT, NYT, WSJ, YOUTUBE | Subscriptions |
| Equinox | EQUINOX | Fitness |
| CLEAR | CLEARME | Travel |
| Hotels | Various | Travel |

### Statement Credit Patterns
| Issuer | Credit Pattern |
|--------|----------------|
| Amex | Negative amount with "CREDIT" in memo |
| Chase | Negative amount, often "SAPPHIRE RESERVE CREDIT" |
| Capital One | Negative amount with "CREDIT" or "BONUS" |

## Output Format

```
YNAB Transaction Analysis
=========================

Potential Benefit Matches Found:

AMEX PLATINUM:
- Jan 5: UBER EATS $25.00 → Uber Cash ($15 monthly limit)
- Jan 8: LULULEMON $89.00 → Lululemon Q1 ($75 remaining)
- Jan 12: DISNEY PLUS $15.99 → Entertainment ($25 limit)

Statement Credits Found:
- Jan 6: STATEMENT CREDIT -$15.00 → Likely Uber Cash
- Jan 13: STATEMENT CREDIT -$15.99 → Likely Entertainment

Unmatched Credits (investigate):
- Jan 10: CREDIT -$50.00 → Unknown source

Recommendations:
- Your Uber Cash spending exceeds the $15 monthly credit
- Consider marking Lululemon Q1 as partially used ($89 spent, $75 credited)
```

## Data Storage

Add YNAB configuration to checklist.json:

```json
{
  "ynab": {
    "budgetId": "last-used",
    "accountMapping": {
      "amex-platinum": "account-uuid-here",
      "chase-sapphire-reserve": "account-uuid-here",
      "capital-one-venture-x": "account-uuid-here",
      "delta-reserve": "account-uuid-here",
      "alaska-atmos-summit": "account-uuid-here"
    },
    "lastSync": "2026-01-15T10:30:00Z"
  }
}
```

## Privacy Notes

- The YNAB token is stored locally only
- Transaction data is processed locally, not sent elsewhere
- Only transaction payee names and amounts are used for matching
