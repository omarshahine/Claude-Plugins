---
description: View and manage learned filing rules
argument-hint: "[--add | --remove | --stats]"
---

# /inbox-triage:rules

View, add, or remove filing rules.

## Usage

```
/inbox-triage:rules          # View all rules
/inbox-triage:rules --add    # Add new rule
/inbox-triage:rules --remove # Remove a rule
/inbox-triage:rules --stats  # Show statistics
```

## Implementation

### View (default)

Read `data/filing-rules.yaml` and display grouped by type and confidence.

### Add (--add)

Use AskUserQuestion to collect:
1. Rule type (domain, email, subject)
2. Pattern value
3. Target folder
4. Initial confidence (default 0.80)

### Remove (--remove)

1. Display rules with IDs
2. Use AskUserQuestion to select
3. Confirm and remove

### Stats (--stats)

Display:
- Accuracy rate
- Top performing rules
- Rules needing review

## Data File

Rules stored in `data/filing-rules.yaml` with:
- Target folder
- Confidence score
- Match count
- Source (bootstrap, user_correction, manual)
