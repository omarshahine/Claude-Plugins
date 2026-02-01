---
description: Deep scan folders and suggest reorganization improvements
argument-hint: "[--folder NAME] [--quick]"
---

# /inbox-triage:optimize

Deep scan existing folders and suggest optimizations: subfolders, rule updates, consolidation.

## Usage

```
/inbox-triage:optimize              # Full analysis of all folders
/inbox-triage:optimize --quick      # Top 10 folders by volume only
/inbox-triage:optimize --folder Travel  # Analyze specific folder
```

## Prerequisites

1. Run `/inbox-triage:setup` first
2. Having existing filing rules helps but is not required

## Implementation

Launch the `folder-optimizer` agent:

```
subagent_type: "inbox-triage:folder-optimizer"
prompt: "Perform deep folder analysis and suggest optimizations."
```

For `--quick`:
```
prompt: "Analyze only the top 10 folders by email count."
```

For `--folder NAME`:
```
prompt: "Perform deep analysis of the [NAME] folder and suggest subfolders or reorganization."
```

## What It Analyzes

| Aspect | Description |
|--------|-------------|
| **Subfolder opportunities** | Large folders that could benefit from subdivision |
| **Rule consistency** | Filing rules that no longer match reality |
| **Missing rules** | Patterns that should have rules |
| **Consolidation** | Low-volume or overlapping folders to merge |
| **Server-side candidates** | Patterns that could be automated at server level |

## Example Output

```
# Folder Optimization Report

## Subfolder Recommendations

### Travel (847 emails)
Suggestion: Create subfolders:
- Flights: aa.com, united.com, delta.com (312 emails)
- Hotels: marriott.com, hyatt.com (285 emails)
- Car Rental: avis.com, hertz.com (156 emails)

## Rule Updates

| Domain | Current | Suggested | Confidence |
|--------|---------|-----------|------------|
| newhotel.com | Archive | Travel/Hotels | 92% |

## Consolidation

| Folder | Emails | Suggestion |
|--------|--------|------------|
| Old Project | 12 | Merge into Archive |
```

## Actions Available

After analysis, you can choose to:
- Create suggested subfolders (emails will be moved)
- Update filing rules
- Merge low-volume folders
- Export server-side rule suggestions
