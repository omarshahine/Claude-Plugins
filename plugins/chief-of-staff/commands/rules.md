---
description: View and manage learned filing rules
---

# /chief-of-staff:rules

View, edit, and manage your learned email filing rules.

## Usage

```
/chief-of-staff:rules              # Show current rules
/chief-of-staff:rules --add        # Add a new rule manually
/chief-of-staff:rules --edit       # Edit existing rules
/chief-of-staff:rules --prune      # Remove low-confidence rules
```

## Arguments

- **--add**: Interactively add a new filing rule
- **--edit**: Edit or delete existing rules
- **--prune**: Remove rules below confidence threshold

## What It Shows

1. **Filing Rules** by type (domain, email, subject pattern)
2. **Confidence scores** and match counts
3. **Delete Patterns** for auto-delete suggestions
4. **Rule Health** - flagged rules needing review

## Example Output

```
Filing Rules Overview
=====================

## Domain Rules (23 rules)
| Domain | → Folder | Confidence | Matches |
|--------|----------|------------|---------|
| chase.com | Financial | 95% | 156 |
| amazon.com | Orders | 92% | 423 |
| united.com | Travel | 88% | 89 |
| github.com | Development | 75% | 234 |
| ... | ... | ... | ... |

## Email Rules (5 rules)
| Email | → Folder | Confidence | Matches |
|-------|----------|------------|---------|
| alerts@chase.com | Financial | 98% | 89 |
| noreply@amazon.com | Orders | 95% | 234 |
| ... | ... | ... | ... |

## Subject Rules (3 rules)
| Pattern | → Folder | Confidence | Matches |
|---------|----------|------------|---------|
| Your.*statement | Financial | 85% | 45 |
| Order.*shipped | Orders | 82% | 78 |
| ... | ... | ... | ... |

## Delete Patterns (8 patterns)
| Domain/Pattern | Category | Confidence |
|----------------|----------|------------|
| newsletter@ | marketing | 90% |
| noreply@social.* | social | 85% |
| ... | ... | ... |

## Rules Needing Review
- newsletters.example.com: 45% confidence (below threshold)
- oldservice.com: No matches in 90 days

Actions:
1. Add new rule
2. Edit existing rule
3. Prune low-confidence rules
4. Export rules
```

## Implementation

This command reads and displays data files directly:

1. Read `~/.claude/data/chief-of-staff/filing-rules.yaml`
2. Read `~/.claude/data/chief-of-staff/delete-patterns.yaml`
3. Format and display tables
4. Use AskUserQuestion for interactive editing
