---
description: Suggest folder reorganization improvements
---

# /inbox-triage:suggest

Propose folder improvements based on learned patterns.

## Usage

```
/inbox-triage:suggest
```

## Implementation

Launch the `organization-analyzer` agent:

```
subagent_type: "inbox-triage:organization-analyzer"
prompt: "Analyze folder structure and suggest improvements: merges, splits, new folders."
```

## Suggestions Include

- **New folders**: High-volume domains without dedicated folders
- **Merges**: Low-volume similar folders
- **Splits**: Mixed-purpose folders
- **Relocations**: Misplaced emails
