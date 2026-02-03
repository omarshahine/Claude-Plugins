---
description: Bootstrap or update filing rules from email patterns
argument-hint: "[--from-history]"
---

# /chief-of-staff:learn

Learn email filing patterns from your existing folder organization or from triage decision history.

## Usage

```
/chief-of-staff:learn                # Bootstrap rules from existing folders
/chief-of-staff:learn --from-history # Learn from triage decision history
```

## Arguments

- **--from-history**: Analyze decision history instead of folder contents

## What It Does

### Bootstrap Mode (default)

1. **Discovers folders** in your email account
2. **Samples emails** from each folder (up to 300 per folder)
3. **Extracts patterns**: sender domains, email addresses, subject patterns
4. **Calculates confidence** based on consistency
5. **Presents rules** for user confirmation via AskUserQuestion
6. **Saves confirmed rules** to `data/filing-rules.yaml`

### From History Mode (--from-history)

1. **Reads decision history** from `data/decision-history.yaml`
2. **Detects patterns** from repeated decisions (3+ occurrences)
3. **Updates confidence scores** based on acceptance rates
4. **Flags underperforming rules** for review
5. **Proposes new rules** for confirmation

## Example Output

### Bootstrap Mode

```
Filing Rules Discovery
======================

Analyzed 12 folders, sampled 2,847 emails.

## High Confidence Rules (>85%)

| Domain | → Folder | Confidence | Emails |
|--------|----------|------------|--------|
| chase.com | Financial | 95% | 156 |
| amazon.com | Orders | 92% | 423 |
| united.com | Travel | 88% | 89 |

## Medium Confidence (70-85%)

| Domain | → Folder | Confidence | Emails |
|--------|----------|------------|--------|
| github.com | Development | 75% | 234 |
| linkedin.com | Social | 72% | 156 |

## Low Confidence (<70%) - Skipped

| Domain | Found in | Reason |
|--------|----------|--------|
| gmail.com | 5 folders | Too scattered |

Which rules would you like to add?
```

### From History Mode

```
Learning from Decision History
==============================

Analyzed 150 decisions from last 30 days.

## Suggestion Accuracy
- Overall: 83% (125/150)
- Archive: 87% (89/102)
- Delete: 95% (19/20)
- Reminder: 64% (18/28)

## Confidence Updates
Boosted (+5%):
- chase.com → Financial (now 95%)
- amazon.com → Orders (now 92%)

Lowered (-15%):
- news.example.com → delete (now 55%)

## New Patterns Detected

1. bestbuy.com → Orders (5 occurrences, 100% consistent)
   Add rule? [Yes/No]

2. notifications@github.com → delete (4 occurrences)
   Add delete pattern? [Yes/No]

## Rules Flagged for Review

- newsletters.example.com: 40% acceptance (below 50% threshold)
  [Keep / Lower confidence / Deprecate]
```

## Implementation

**Bootstrap Mode:**
```
subagent_type: "chief-of-staff:pattern-learner"
prompt: "Bootstrap filing rules from existing email folder organization. Sample emails from each folder and extract domain patterns."
```

**From History Mode:**
```
subagent_type: "chief-of-staff:decision-learner"
prompt: "Analyze decision history and propose rule updates. Update confidence scores and detect new patterns."
```
