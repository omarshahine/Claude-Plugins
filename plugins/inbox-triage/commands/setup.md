---
description: Configure email provider for inbox-triage
---

# /inbox-triage:setup

Configure the email provider and verify connectivity.

## What This Command Does

1. Verify email provider connectivity
2. Discover folder structure
3. Update settings with setup timestamp

## Implementation

1. Read `data/settings.yaml` for active provider
2. Use ToolSearch to load email MCP tools: `+fastmail list mailboxes`
3. Call list_mailboxes to verify connection
4. Display folder structure
5. Update `data/settings.yaml` with setup_date

## Output

```
# inbox-triage Setup Complete

## Email Provider
- Provider: [provider name]
- Connection: Success

## Folder Structure
Discovered N folders:
[folder list]

## Next Steps
1. Run `/inbox-triage:learn` to bootstrap filing rules
2. Run `/inbox-triage:triage` to process inbox
```
