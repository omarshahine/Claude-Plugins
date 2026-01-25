---
description: Configure email and reminder providers for inbox-to-reminder
---

# /inbox-to-reminder:setup

Configure your email and reminder providers for the inbox-to-reminder plugin.

## What This Does

1. Checks for required MCP servers (email provider, Apple PIM)
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

### Step 2: Check for Apple PIM

The Apple PIM plugin provides Apple Reminders integration. Check if `apple-pim` is available.

If not found:
```
Apple PIM not found. Install with:
  /plugin install apple-pim@claude-plugins-official
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

### Step 4: Gather Customizations

The plugin can be personalized for your household. Use Claude memory to pre-populate known values, then ask for confirmation.

**Check Claude Memory First:**
Look for known information about the user:
- User's name
- Partner name
- Family members' names

**Then use AskUserQuestion to confirm:**

```
Tool: AskUserQuestion
Parameters:
  questions: [
    {
      question: "What is your partner's name? (for filtering 'emails from my partner')",
      header: "Partner",
      multiSelect: false,
      options: [
        { label: "[name from memory]", description: "Use this name (Recommended)" },
        { label: "Skip", description: "Don't set up partner filtering" }
      ]
    },
    {
      question: "Which reminder list do you use for family tasks?",
      header: "Family List",
      multiSelect: false,
      options: [
        { label: "Family", description: "Default list name" },
        { label: "Home", description: "Alternative name" },
        { label: "Household", description: "Alternative name" }
      ]
    }
  ]
```

If memory doesn't have partner name, the options should just be:
- "Enter name" (let user type via "Other")
- "Skip" (don't set up partner filtering)

### Step 5: Save Configuration

Update `data/settings.local.yaml` (create if it doesn't exist):

```yaml
providers:
  email:
    active: [selected provider]
    # ... mappings stay the same

  reminders:
    active: apple-pim
    # ... mappings stay the same

customizations:
  user_name: [from memory or null]
  partner_name: [from user selection or null]
  family_list_name: [from user selection]
  family_members: []

setup_date: "YYYY-MM-DD"
```

### Step 6: Confirm Setup

Display confirmation message:
```
inbox-to-reminder configured successfully!

Email Provider: [provider]
Reminder Provider: Apple PIM
Partner Name: [name or "not set"]
Family List: [list name]

Run /inbox-to-reminder:scan to start scanning your inbox for action items.
```

## Implementation

Use these tools:
- `Bash` with `claude mcp list` to check installed MCP servers
- `AskUserQuestion` to prompt for provider selection
- `Read` to load current settings.yaml
- `Write` to save updated settings.yaml
