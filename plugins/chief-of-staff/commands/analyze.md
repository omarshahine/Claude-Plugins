---
description: Analyze Trash and Archive for organization insights
---

# /chief-of-staff:analyze

Analyze your Trash and Archive patterns to find unsubscribe candidates, misplaced emails, and folder optimization opportunities.

## Usage

```
/chief-of-staff:analyze
```

## What It Does

1. **Trash Analysis**
   - Samples recent deleted emails (500 or 30 days)
   - Identifies frequently deleted domains
   - Finds newsletters deleted without reading
   - Suggests unsubscribe candidates

2. **Archive Analysis**
   - Samples recent archived emails (500 or 90 days)
   - Finds emails that belong in existing folders
   - Identifies domains needing dedicated folders

3. **Generates Report**
   - Unsubscribe candidates
   - Delete pattern categories
   - Misplaced email suggestions
   - New folder opportunities

4. **Offers Actions**
   - Run newsletter-unsubscriber for candidates
   - Move misplaced emails
   - Create suggested folders

## Example Output

```
Email Organization Analysis
===========================

## Trash Patterns

### Unsubscribe Candidates (5+ deletions)
| Domain | Deleted | Read? | Unsubscribe? |
|--------|---------|-------|--------------|
| deals.example.com | 23 | Never | Available |
| newsletter.spam.com | 18 | Never | Available |
| promo.retailer.com | 12 | Rarely | Available |

### Delete Pattern Categories
- Newsletters: 45 emails (15 domains)
- Social notifications: 23 emails (3 domains)
- Calendar acceptances: 12 emails

## Archive Analysis

### Misplaced Emails
Found 8 emails in Archive that belong elsewhere:
- 3 from chase.com → should be in Financial
- 2 from united.com → should be in Travel
- 3 from amazon.com → should be in Orders

### New Folder Suggestions
| Domain | Count | Current | Suggested |
|--------|-------|---------|-----------|
| github.com | 156 | Archive | Development |
| linkedin.com | 89 | Archive | Social |

## Recommendations

1. Unsubscribe from 3 newsletters you consistently delete
2. Move 8 misplaced emails to correct folders
3. Consider creating a "Development" folder for github.com

Would you like me to:
1. Run newsletter-unsubscriber for candidates
2. Move misplaced emails
3. Create suggested folders
4. Skip all
```

## Implementation

```
subagent_type: "chief-of-staff:organization-analyzer"
prompt: "Analyze Trash and Archive patterns. Sample recent emails and generate optimization report."
```
