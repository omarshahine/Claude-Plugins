---
description: Bootstrap filing rules from existing folder organization
argument-hint: "[--quick]"
---

# /inbox-triage:learn

Analyze existing folder organization to extract filing patterns.

## Usage

```
/inbox-triage:learn          # Full analysis
/inbox-triage:learn --quick  # Top 10 folders only
```

## Implementation

Launch the `pattern-learner` agent:

```
subagent_type: "inbox-triage:pattern-learner"
prompt: "Analyze all email folders and extract filing patterns. Present rules for user confirmation."
```

For --quick:
```
prompt: "Analyze the top 10 most-used folders only."
```

## What It Does

1. Samples emails from each folder (up to 200)
2. Extracts sender domain patterns
3. Calculates confidence scores
4. Presents rules for confirmation
5. Saves approved rules
