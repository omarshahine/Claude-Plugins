---
description: Initialize or configure credit card benefits tracking
argument-hint: "[card-name] [--open-date YYYY-MM-DD]"
allowed-tools:
  - Read
  - Write
  - Bash
---

# Setup Credit Card Benefits Tracker

Initialize the benefits tracking system or configure individual cards.

## Data Location

```
~/.config/credit-card-benefits/checklist.json
```

## Operations

### Initial Setup

If no checklist exists, create the config directory and initialize from template:

```bash
mkdir -p ~/.config/credit-card-benefits
```

Then copy the template from the plugin's data directory to the user's config location.

### Configure Card Open Date

To track anniversary-based benefits correctly, the user needs to set their card open date:

```
/credit-card-benefits:setup venture-x --open-date 2023-06-15
```

Update the `accountOpenDate` field for the specified card.

### Add/Remove Cards

Users may not have all cards. Allow them to:
- Remove cards they don't have: `--remove card-name`
- The checklist template includes all cards; remove unwanted ones

### Card Name Aliases

Support these aliases:
- `amex-platinum`, `amex`, `platinum` → amex-platinum
- `venture-x`, `venturex`, `capital-one` → capital-one-venture-x
- `sapphire-reserve`, `sapphire`, `chase` → chase-sapphire-reserve
- `alaska-atmos`, `alaska`, `atmos`, `summit` → alaska-atmos-summit
- `delta-reserve`, `delta` → delta-reserve

## Interactive Setup

If run without arguments, walk the user through:

1. **Which cards do you have?** (multi-select)
2. **What is your card open date?** (for each card, for anniversary calculations)
3. **Do you have any selected airline for Amex Platinum?**
4. **Do you have bank relationship bonus for Alaska Atmos?**

## Example Output

```
Credit Card Benefits Tracker initialized!

Tracking 3 cards:
- American Express Platinum (opened: 2022-03-15)
- Chase Sapphire Reserve (opened: 2021-08-01)
- Capital One Venture X (opened: 2023-06-15)

Run `/credit-card-benefits:status` to see your current benefit status.
```

## File Creation

When creating the checklist, update the `lastUpdated` timestamp and set appropriate defaults.
