# newsletter-unsubscriber

Scan your inbox for newsletters and help you unsubscribe from unwanted ones.

## Features

- Detects newsletters using RFC 2369 email headers (List-Unsubscribe)
- Maintains an allowlist of newsletters you want to keep
- Tracks previously unsubscribed senders to flag repeat offenders
- Executes unsubscribes via mailto or web forms (Playwright)
- Organizes processed emails to a dedicated folder
- Supports multiple email providers (Fastmail, Gmail, Outlook)

## Setup

Run the setup command to configure your email provider:

```
/newsletter-unsubscriber:setup
```

## Usage

```
/newsletter-unsubscriber:unsubscribe
```

## Requirements

### MCP Servers

- **Email Provider** (one of):
  - `fastmail` - Fastmail MCP server
  - `gmail` - Gmail MCP server (via Smithery)
  - `outlook` - Outlook MCP server (via Smithery)

- **Browser Automation**:
  - `playwright` - For web-based unsubscribe forms (bundled in plugin)

## Configuration

Provider settings are stored in `data/settings.yaml`. The setup command will configure this for you.

## Data Files

- `data/newsletter-lists.yaml` - Your allowlist and unsubscribed senders
- `data/newsletter-patterns.json` - Detection patterns for newsletters
- `data/settings.yaml` - Provider configuration

## How It Works

1. **Loads your lists** - Reads allowlist and previously unsubscribed senders
2. **Scans inbox** for newsletters (using List-Unsubscribe header)
3. **Flags repeat offenders** - Highlights senders who ignored previous unsubscribes
4. **Groups newsletters** by sender domain with frequency counts
5. **Asks which to unsubscribe** - You select via interactive prompts
6. **Executes unsubscribes** via mailto or web forms
7. **Asks about allowlist** - Offers to add skipped newsletters to allowlist
8. **Updates your lists** - Tracks unsubscribed senders + allowlist additions
9. **Organizes emails** by moving them to Unsubscribed folder

## Unsubscribe Methods

| Method | How It Works |
|--------|--------------|
| Mailto | Sends "unsubscribe" email to the list address |
| Web Form (simple) | Clicks "Unsubscribe" button on page |
| Web Form (email) | Enters your email and submits |
| Web Form (multi-step) | Follows through confirmation pages |

## Failure Scenarios

Some unsubscribes may fail and require manual action:

| Issue | What Happens |
|-------|--------------|
| CAPTCHA | Provides URL for manual unsubscribe |
| Login required | Provides URL for manual unsubscribe |
| Timeout | Retries once, then reports failure |
