---
description: Show detailed information about a credit card's benefits
argument-hint: "<card-name>"
allowed-tools:
  - Read
---

# Credit Card Benefits Information

Display detailed information about a specific credit card's benefits, how to use them, and tips for maximizing value.

## Usage

```
/credit-card-benefits:info <card-name>
```

## Card Documentation Location

Read from the plugin's cards directory:
- `cards/amex-platinum.md`
- `cards/capital-one-venture-x.md`
- `cards/chase-sapphire-reserve.md`
- `cards/alaska-atmos.md`
- `cards/delta-reserve.md`

## Card Name Aliases

- `amex`, `platinum`, `amex-platinum` → amex-platinum.md
- `venture-x`, `venturex`, `capital-one` → capital-one-venture-x.md
- `chase`, `sapphire`, `sapphire-reserve` → chase-sapphire-reserve.md
- `alaska`, `atmos` → alaska-atmos.md
- `delta`, `delta-reserve` → delta-reserve.md

## Output

Display the card documentation which includes:
- Annual fee
- Reset type information
- All statement credits with amounts and reset periods
- Lounge access details
- Points earning structure
- Travel benefits
- Tips and strategies

## Examples

```
/credit-card-benefits:info amex
/credit-card-benefits:info chase
/credit-card-benefits:info venture-x
```

## Special 2026 Information

When displaying Chase Sapphire Reserve info, highlight:
- The one-time 2026 Select Hotels credit ($250)
- Credit stacking opportunity (up to $800 on one trip)

When displaying Capital One Venture X info, highlight:
- February 2026 lounge policy changes
- Guest fee structure
