## Email Provider Initialization (Standard Pattern)

**This agent requires an email MCP server.** Copy this section to agents that need email access.

### Step 1: Find Plugin Data Directory

Use Glob to locate the settings file:
```
Glob: ~/.claude/plugins/cache/*/chief-of-staff/*/data/settings.yaml
```

Extract the data directory path from the result (everything up to `/data/`).

### Step 2: Read Settings and Get Tool Mappings

Read `settings.yaml` and extract:
```yaml
providers:
  email:
    active: fastmail  # or gmail, outlook
    mappings:
      fastmail:
        list_mailboxes: mcp__fastmail__list_mailboxes
        list_emails: mcp__fastmail__list_emails
        # ... etc
```

**Store these values:**
- `EMAIL_PROVIDER` = `providers.email.active` (e.g., "fastmail")
- `EMAIL_TOOLS` = `providers.email.mappings[EMAIL_PROVIDER]`

### Step 3: Load Email Tools via ToolSearch

Load the email provider's tools:
```
ToolSearch query: "+{EMAIL_PROVIDER}"
```

Example: If `EMAIL_PROVIDER` is "fastmail", search for `+fastmail`.

### Step 4: Verify Required Tools

Check that these core tools exist in `EMAIL_TOOLS`:
- `list_mailboxes` - Required for folder discovery
- `list_emails` - Required for fetching emails
- `get_email` - Required for reading email content

**If tools missing**, display:
```
⚠️ Email provider "{EMAIL_PROVIDER}" not fully configured!

Missing tool mappings in settings.yaml. Required:
- list_mailboxes
- list_emails
- get_email

Check your settings.yaml providers.email.mappings section.
```

### Step 5: Use Mapped Tool Names

Throughout the agent, reference tools via the mappings:

**CORRECT** (use mapping):
```
Call EMAIL_TOOLS.list_mailboxes
Call EMAIL_TOOLS.list_emails with mailboxId: "inbox-id"
Call EMAIL_TOOLS.bulk_move with emailIds: [...], mailboxId: "target"
```

**INCORRECT** (hardcoded):
```
Call mcp__fastmail__list_mailboxes  ← DON'T DO THIS
```

### Error: No Email Provider

If ToolSearch finds no email tools, display:
```
⚠️ No email provider configured!

Run `/chief-of-staff:setup` to configure your email provider.

The setup wizard will:
1. Guide you through adding your email MCP server (Cowork or CLI)
2. Create the settings.yaml configuration
3. Verify your connection works

Supported providers: Fastmail, Gmail, Outlook
```

---

## Quick Reference: Email Tool Operations

| Operation | Description | Common Parameters |
|-----------|-------------|-------------------|
| `list_mailboxes` | Get all folders/mailboxes | (none) |
| `list_emails` | List emails in a folder | `mailboxId`, `limit` |
| `get_email` | Get single email details | `emailId` |
| `search_emails` | Simple search | `query` |
| `advanced_search` | Complex search with filters | `mailboxId`, `from`, `after`, etc. |
| `move_email` | Move single email | `emailId`, `mailboxId` |
| `bulk_move` | Move multiple emails | `emailIds[]`, `mailboxId` |
| `delete_email` | Delete single email | `emailId` |
| `bulk_delete` | Delete multiple emails | `emailIds[]` |
| `flag_email` | Star/flag an email | `emailId`, `flagged` |
| `bulk_flag` | Flag multiple emails | `emailIds[]`, `flagged` |
| `send_email` | Send new email | `to`, `subject`, `body` |
| `reply_to_email` | Reply to thread | `emailId`, `body` |
| `get_thread` | Get conversation thread | `threadId` |
| `get_email_attachments` | List email attachments (optional) | `emailId` |
| `download_attachment` | Download attachment content (optional) | `emailId`, `attachmentId` |
