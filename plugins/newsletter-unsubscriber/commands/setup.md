---
description: Configure email provider for newsletter-unsubscriber
---

# /newsletter-unsubscriber:setup

Configure your email provider for the newsletter-unsubscriber plugin.

## What This Does

1. Checks for required MCP servers (email provider, Playwright)
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

### Step 2: Check for Playwright

Playwright is bundled with this plugin via `.mcp.json`. It should be available automatically.

If not working, the user may need to install the Playwright MCP server:
```
npm install -g @playwright/mcp
```

### Step 3: Ask User for Email Provider Selection

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

### Step 4: Save Configuration

Update `data/settings.local.yaml` (create if it doesn't exist):

```yaml
providers:
  email:
    active: [selected provider]
    # ... mappings stay the same

setup_date: "YYYY-MM-DD"
```

### Step 5: Confirm Setup

Display confirmation message:
```
newsletter-unsubscriber configured successfully!

Email Provider: [provider]
Browser Automation: Playwright (bundled)

Run /newsletter-unsubscriber:unsubscribe to start cleaning up newsletters.
```

## Implementation

Use these tools:
- `Bash` with `claude mcp list` to check installed MCP servers
- `AskUserQuestion` to prompt for provider selection
- `Read` to load current settings.yaml
- `Write` to save updated settings.yaml
