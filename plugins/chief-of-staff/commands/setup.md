---
description: Configure Chief-of-Staff email provider and integrations
---

# /chief-of-staff:setup

Configure your email provider and verify all integrations are working.

## What This Command Does

1. Verify email provider connectivity (Fastmail, Gmail, or Outlook)
2. Discover folder structure
3. Verify optional integrations:
   - Parcel API (for package tracking)
   - Apple PIM (for reminders)
   - Playwright (for newsletter unsubscribe)
4. Create initial settings files

## Implementation

1. Read `data/settings.example.yaml` to get the template
2. Ask user which email provider they're using via AskUserQuestion
3. Use ToolSearch to load email MCP tools (e.g., `+fastmail list mailboxes`)
4. Call list_mailboxes to verify connection
5. Check optional integrations:
   - Try to load parcel-api tools
   - Try to load apple-pim tools
   - Try to load playwright tools
6. Create `data/settings.yaml` with discovered configuration
7. Display folder structure and integration status

## Questions to Ask

```
AskUserQuestion:
  questions:
    - question: "Which email provider are you using?"
      header: "Email"
      options:
        - label: "Fastmail (Recommended)"
          description: "Full MCP integration with advanced search"
        - label: "Gmail"
          description: "Gmail MCP server required"
        - label: "Outlook"
          description: "Microsoft Graph MCP required"
```

## Output

```
# Chief-of-Staff Setup Complete

## Email Provider
- Provider: Fastmail
- Connection: ✓ Success
- Folders: 42 discovered

## Integrations
- Parcel API: ✓ Connected (package tracking enabled)
- Apple PIM: ✓ Connected (reminders enabled)
- Playwright: ✓ Available (newsletter unsubscribe enabled)

## Folder Structure
Key folders discovered:
- Inbox
- Archive
- Orders
- Financial
- Travel
...

## Next Steps
1. Run `/chief-of-staff:learn` to bootstrap filing rules
2. Run `/chief-of-staff:triage` to process your inbox interactively
3. Run `/chief-of-staff:status` for a quick dashboard
```
