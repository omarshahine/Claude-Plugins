---
description: Deep scan folders and suggest reorganization
---

# /chief-of-staff:optimize

Perform a deep analysis of your email folder structure and suggest optimizations.

## Usage

```
/chief-of-staff:optimize
```

## What It Does

1. **Folder Analysis**
   - Samples emails from folders with 50+ emails
   - Extracts domain distributions
   - Identifies mixed-purpose folders

2. **Subfolder Suggestions**
   - Finds folders that could benefit from subfolders
   - Identifies domain clusters (e.g., airlines vs hotels in Travel)

3. **Rule Consistency Check**
   - Compares folder contents against filing rules
   - Finds stale or conflicting rules

4. **Consolidation Opportunities**
   - Identifies low-volume folders
   - Finds folders with overlapping domains

## Example Output

```
Folder Optimization Report
==========================

## Summary
- Folders analyzed: 24
- Emails sampled: 4,521
- Suggestions: 6

## Subfolder Recommendations

### Travel (847 emails)
**Current state:** Mixed content from 12 domains
**Suggestion:** Create subfolders:
- Airlines: aa.com, united.com, delta.com (312 emails)
- Hotels: marriott.com, hyatt.com, hilton.com (285 emails)
- Car Rental: avis.com, hertz.com (156 emails)
**Benefit:** Easier navigation, better filing rules

### Finance (634 emails)
**Current state:** Mixed financial emails
**Suggestion:** Create subfolders:
- Banking: chase.com, wellsfargo.com (289 emails)
- Investments: schwab.com, fidelity.com (198 emails)
- Bills: utilities, subscriptions (147 emails)

## Rule Updates Suggested

### New Rules
| Domain | Folder | Confidence |
|--------|--------|------------|
| netflix.com | Subscriptions | 95% |
| spotify.com | Subscriptions | 92% |

### Stale Rules (no longer match)
| Domain | Rule → | Actual → | Action |
|--------|--------|----------|--------|
| oldservice.com | Archive | (not found) | Delete |

## Consolidation Opportunities

### Low-Volume Folders
| Folder | Emails | Last Activity | Suggestion |
|--------|--------|---------------|------------|
| Old Project | 8 | 6 months ago | Merge to Archive |
| Misc | 12 | 2 months ago | Review & distribute |

Would you like me to:
1. Create suggested subfolders and move emails
2. Update filing rules
3. Consolidate low-volume folders
4. Show detailed analysis
```

## Implementation

```
subagent_type: "chief-of-staff:folder-optimizer"
prompt: "Perform deep folder analysis and generate optimization report."
```
