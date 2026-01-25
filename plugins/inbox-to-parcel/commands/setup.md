---
description: Configure email and package tracking providers for inbox-to-parcel
---

# /inbox-to-parcel:setup

Configure your email and package tracking providers for the inbox-to-parcel plugin.

## What This Does

1. Checks for required MCP servers (email provider, Parcel API, Playwright)
2. Shows installation commands if any are missing
3. Asks you to select your email provider
4. Saves configuration to `data/settings.yaml`

## Setup Process

### Step 1: Check for Email Provider MCP

Check if the user has an email MCP server configured. Use `claude mcp list` via Bash to check.

**Supported Email Providers:**

| Provider | How to Check | Installation |
|----------|--------------|--------------|
| Fastmail | Look for `fastmail` in mcp list | Custom MCP server |
| Gmail | Look for `gmail` in mcp list | `npx -y @smithery/cli@latest install gmail --client claude` |
| Outlook | Look for `outlook` in mcp list | `npx -y @smithery/cli@latest install outlook --client claude` |

If no email provider is found, display:
```
No email MCP server found. Please install one:

For Gmail:
  npx -y @smithery/cli@latest install gmail --client claude

For Outlook:
  npx -y @smithery/cli@latest install outlook --client claude

For Fastmail:
  (Custom setup required - see documentation)
```

### Step 2: Check for Parcel API MCP

Look for `parcel` in the MCP list.

If not found, display:
```
Parcel API MCP not found. Install with:
  npx -y @smithery/cli@latest install @NOVA-3951/parcel-api-mcp --client claude

You'll need your Parcel API key from:
  https://web.parcelapp.net/#apiPanel
```

### Step 3: Check for Playwright

Playwright is bundled with this plugin via `.mcp.json`. It should be available automatically.

If not working, the user may need to install the Playwright MCP server:
```
npm install -g @playwright/mcp
```

### Step 4: Ask User for Email Provider Selection

Use AskUserQuestion to ask which email provider to use:

```
Tool: AskUserQuestion
Parameters:
  questions: [{
    question: "Which email provider would you like to use?",
    header: "Email",
    multiSelect: false,
    options: [
      { label: "Fastmail", description: "Use Fastmail MCP" },
      { label: "Gmail", description: "Use Gmail MCP" },
      { label: "Outlook", description: "Use Outlook/Microsoft 365 MCP" }
    ]
  }]
```

### Step 5: Save Configuration

Update `data/settings.local.yaml` (create if it doesn't exist):

```yaml
providers:
  email:
    active: [selected provider]
    # ... mappings stay the same

  parcel:
    active: parcel-api
    # ... mappings stay the same

setup_date: "YYYY-MM-DD"
```

### Step 6: Confirm Setup

Display confirmation message:
```
inbox-to-parcel configured successfully!

Email Provider: [provider]
Package Tracking: Parcel API
Browser Automation: Playwright (bundled)

Run /inbox-to-parcel:track to start processing shipping emails.
```

## Implementation

Use these tools:
- `Bash` with `claude mcp list` to check installed MCP servers
- `AskUserQuestion` to prompt for provider selection
- `Read` to load current settings.yaml
- `Write` to save updated settings.yaml
