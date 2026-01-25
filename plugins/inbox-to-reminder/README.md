# inbox-to-reminder

Scan your email inbox for action items and create reminders in Apple Reminders.

## Features

- Scans inbox for emails containing action items (bills, tasks, deadlines)
- Identifies different types of tasks: bills/payments, meetings, follow-ups, deadlines
- Creates reminders with appropriate due dates and context
- Organizes reminders into the correct lists (Budget & Finances, Travel, etc.)
- Supports multiple email providers (Fastmail, Gmail, Outlook)

## Setup

Run the setup command to configure your email provider:

```
/inbox-to-reminder:setup
```

## Usage

```
/inbox-to-reminder:scan                    # Scan recent inbox (7 days)
/inbox-to-reminder:scan partner            # Scan emails from partner
/inbox-to-reminder:scan --days 30          # Scan last 30 days
/inbox-to-reminder:scan bills              # Search for bills/invoices
```

## Requirements

### MCP Servers

- **Email Provider** (one of):
  - `fastmail` - Fastmail MCP server
  - `gmail` - Gmail MCP server (via Smithery)
  - `outlook` - Outlook MCP server (via Smithery)

- **Reminders**:
  - `apple-pim` - Apple PIM plugin for Apple Reminders

## Configuration

Provider settings are stored in `data/settings.yaml`. The setup command will configure this for you.

### Customizations

During setup, you can personalize the plugin for your household:

| Setting | Description |
|---------|-------------|
| `partner_name` | Your partner's name for filtering "emails from my partner" |
| `family_list_name` | Your Apple Reminders list for family tasks (e.g., "Family", "Home") |
| `family_members` | Additional family member names for filtering |

The setup command will attempt to pre-populate these from Claude's memory about you.

## How It Works

1. **Scans** inbox for emails containing action items
2. **Identifies** tasks, bills, deadlines, and follow-ups
3. **Presents** found items for your selection (via AskUserQuestion)
4. **Creates** reminders in the appropriate Apple Reminders lists

## Types of Action Items Detected

- **Bills/Payments**: Invoices, statements, payment due dates
- **Meetings/Events**: RSVPs, calendar items, scheduling requests
- **Tasks**: To-dos, follow-ups, things to complete
- **Deadlines**: Time-sensitive items with specific due dates
- **Administrative**: Forms to fill, documents to sign, registrations
