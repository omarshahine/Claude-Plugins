---
description: Check for updated credit card benefits and apply changes to checklist
argument-hint: "[card-name] [--all] [--dry-run]"
allowed-tools:
  - Read
  - Write
  - Edit
  - WebSearch
  - WebFetch
  - AskUserQuestion
---

# Update Credit Card Benefits

Research current credit card benefits from reputable sources and update your checklist with any changes.

## Usage

```
/credit-card-benefits:update [options]
```

### Options

- `<card-name>` - Update specific card (e.g., `amex-platinum`, `chase-sapphire-reserve`)
- `--all` - Update all enabled cards
- `--dry-run` - Show proposed changes without applying them

## How It Works

### Step 1: Research Current Benefits

For each card, search reputable sources:

**Primary Sources (Official):**
- americanexpress.com (Amex cards)
- chase.com (Chase cards)
- capitalone.com (Capital One cards)
- bankofamerica.com (Alaska cards)

**Secondary Sources (Analysis):**
- thepointsguy.com
- nerdwallet.com
- doctorofcredit.com
- upgradedpoints.com

**Search Queries:**
```
"{card name} benefits {current year}"
"{card name} statement credits {current year}"
"{card name} new benefits changes"
```

### Step 2: Compare Against Current Checklist

Parse research results and compare to existing benefits:

```
Analyzing American Express Platinum...

Current checklist has:
- Hotel Credit: $300 semi-annual
- Resy Credit: $100 quarterly
- Lululemon: $75 quarterly
- Digital Entertainment: $25/month
- Uber Cash: $15/month + $20 Dec
- Airline Fee: $200/year
- Saks: $50 semi-annual
- Equinox: $25/month
- CLEAR+: $209/year
- Global Entry: $120 every 4 years

Research found:
- Hotel Credit: $300 semi-annual ✓ (unchanged)
- Resy Credit: $100 quarterly ✓ (unchanged)
- Lululemon: $75 quarterly ✓ (unchanged)
- Digital Entertainment: $25/month ✓ (unchanged)
- Uber Cash: $15/month + $20 Dec ✓ (unchanged)
- Airline Fee: $200/year ✓ (unchanged)
- Saks: $50 semi-annual ✓ (unchanged)
- Equinox: $25/month ✓ (unchanged)
- CLEAR+: $209/year ✓ (unchanged)
- Global Entry: $120 every 4 years ✓ (unchanged)
- NEW: Walmart+ membership ($12.95/month credit)
```

### Step 3: Present Changes for Approval

Use AskUserQuestion to get approval for each change:

**For New Benefits:**
```
NEW BENEFIT FOUND: Walmart+ Membership Credit

Source: thepointsguy.com, americanexpress.com
Details:
- Amount: $12.95/month ($155.40/year)
- Period: Monthly
- How to use: Enroll in Walmart+ using your Platinum card

Add this benefit to your checklist?
[ ] Yes, add it
[ ] No, skip it
[ ] I don't have this benefit (older card version)
```

**For Removed Benefits:**
```
BENEFIT MAY BE DISCONTINUED: Example Old Benefit

This benefit was not found in current research.
Possible reasons:
- Benefit was discontinued
- Benefit was replaced by something else
- Research may have missed it

What would you like to do?
[ ] Remove from checklist (benefit is gone)
[ ] Keep in checklist (I still have it)
[ ] Mark as grandfathered (old cardholders only)
```

**For Changed Benefits:**
```
BENEFIT CHANGED: Airline Fee Credit

Previous: $200/year for incidental fees
Updated: $200/year - now includes seat upgrades, in-flight purchases

Source: americanexpress.com
Effective: January 2026

Update the benefit description?
[ ] Yes, update it
[ ] No, keep current description
```

**For Amount Changes:**
```
AMOUNT CHANGED: Annual Fee

Previous: $695/year
Updated: $895/year

Source: americanexpress.com
Effective: For renewals after January 2, 2026

Update the annual fee?
[ ] Yes, update to $895
[ ] No, keep at $695 (my fee hasn't changed yet)
```

### Step 4: Apply Approved Changes

After all approvals collected, apply changes to checklist.yaml:

```
Applying changes to checklist...

✓ Added: walmart-plus credit ($12.95/month)
✓ Updated: Annual fee changed to $895
✓ Updated: Airline fee description expanded
✗ Skipped: User declined to add new benefit X

Changes saved to ~/.config/credit-card-benefits/checklist.yaml

Tip: Run /credit-card-benefits:status to see your updated benefits
```

## Research Strategy

### For Each Card

1. **Search for official page:**
   ```
   WebSearch: "{card name} card benefits site:{issuer}.com"
   ```

2. **Search for recent changes:**
   ```
   WebSearch: "{card name} new benefits {year}"
   WebSearch: "{card name} benefits changes {year}"
   ```

3. **Fetch and parse results:**
   ```
   WebFetch: Official card benefits page
   Extract: Credit amounts, periods, eligibility
   ```

4. **Cross-reference with analysis sites:**
   ```
   WebFetch: TPG or NerdWallet card review
   Verify: Amounts match, look for additional details
   ```

### Trusted Sources by Card

| Card | Official Source | Analysis Sources |
|------|-----------------|------------------|
| Amex Platinum | americanexpress.com/us/credit-cards/card/platinum | thepointsguy.com, nerdwallet.com |
| Venture X | capitalone.com/credit-cards/venture-x | thepointsguy.com, nerdwallet.com |
| Sapphire Reserve | chase.com/personal/credit-cards/sapphire-reserve | thepointsguy.com, doctorofcredit.com |
| Alaska Atmos | bankofamerica.com/credit-cards/alaska-airlines | thepointsguy.com, frequentmiler.com |
| Delta Reserve | americanexpress.com/us/credit-cards/card/delta-skymiles-reserve | thepointsguy.com, nerdwallet.com |

## Output Format

### Dry Run Output

```
/credit-card-benefits:update amex-platinum --dry-run

Researching American Express Platinum benefits...

Sources checked:
✓ americanexpress.com - Official benefits page
✓ thepointsguy.com - Recent review (Jan 2026)
✓ nerdwallet.com - Card guide

Proposed Changes:
─────────────────

NEW BENEFITS:
1. Walmart+ Credit - $12.95/month
   Source: americanexpress.com

CHANGED BENEFITS:
1. Annual Fee - $695 → $895
   Effective: Renewals after Jan 2, 2026

UNCHANGED BENEFITS: 15
REMOVED BENEFITS: 0

Run without --dry-run to apply changes with approval prompts.
```

### Change Log

After updates, add to checklist:

```yaml
updateHistory:
  - date: 2026-01-22
    card: amex-platinum
    changes:
      - type: added
        benefit: walmart-plus
        details: "$12.95/month credit"
      - type: modified
        benefit: annual-fee
        from: 695
        to: 895
    sources:
      - americanexpress.com
      - thepointsguy.com
```

## Error Handling

### Source Unavailable
```
Warning: Could not fetch americanexpress.com/platinum
Falling back to cached data and secondary sources.

Last known update: 2025-12-15
Continue with available sources? [y/n]
```

### Conflicting Information
```
Warning: Sources disagree on Resy credit amount

americanexpress.com: $100/quarter
thepointsguy.com: $100/quarter
outdated-blog.com: $50/quarter (dated 2024)

Using official source (americanexpress.com): $100/quarter
```

### No Changes Found
```
No changes found for American Express Platinum.

Last checked: 2026-01-22
Your checklist is up to date.

Tip: Benefits typically change in January or at card refresh announcements.
```

## Scheduling Recommendations

Benefits typically change:
- **January**: Calendar year resets, new annual benefits
- **Card refresh announcements**: Major overhauls (like Amex Platinum 2025)
- **Mid-year**: Occasional additions or modifications

Recommended update frequency:
- Monthly during Q1 (January-March)
- Quarterly rest of year
- Immediately after major card announcements
