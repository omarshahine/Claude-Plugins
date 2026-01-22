---
description: Show status of all credit card benefits and unused credits
argument-hint: "[card-name] [--expiring] [--unused]"
allowed-tools:
  - Read
  - Bash
---

# Credit Card Benefits Status

Show the current status of credit card benefits tracking.

## Usage

When the user runs this command, read the checklist data and display benefit status.

### Data Location

```
~/.config/credit-card-benefits/checklist.json
```

### Arguments

- **card-name** (optional): Filter to specific card
  - `amex-platinum` or `amex` or `platinum`
  - `venture-x` or `venturex` or `capital-one`
  - `sapphire-reserve` or `sapphire` or `chase`
  - `alaska-atmos` or `alaska` or `atmos`
  - `delta-reserve` or `delta`
- **--expiring**: Show only benefits expiring within 30 days
- **--unused**: Show only benefits that haven't been fully used

### Output Format

Display a summary table for each card showing:

| Benefit | Amount | Used | Remaining | Resets | Days Left |
|---------|--------|------|-----------|--------|-----------|

Calculate:
- **Days Left**: Days until the benefit resets/expires
- **% of Fee Recovered**: Sum of used credits vs annual fee

### Examples

```
/credit-card-benefits:status
/credit-card-benefits:status amex
/credit-card-benefits:status --expiring
/credit-card-benefits:status chase --unused
```

### If No Data Exists

If the checklist file doesn't exist:
1. Inform the user no tracking data was found
2. Offer to create the checklist: "Run `/credit-card-benefits:setup` to initialize your benefits tracker"

### Calculations

For monthly benefits, calculate which months have been used:
- Current month: January = 1, check if monthsUsed includes current month

For quarterly benefits:
- Q1: Jan-Mar (resets Jan 1)
- Q2: Apr-Jun (resets Apr 1)
- Q3: Jul-Sep (resets Jul 1)
- Q4: Oct-Dec (resets Oct 1)

For semi-annual:
- H1: Jan-Jun (resets Jan 1)
- H2: Jul-Dec (resets Jul 1)

For anniversary-based, calculate from accountOpenDate.
