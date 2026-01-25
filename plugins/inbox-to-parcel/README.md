# inbox-to-parcel

Process shipping notification emails and add tracking to Parcel app.

## Features

- Scans inbox for shipment notification emails
- Extracts tracking numbers and carrier information
- Uses Playwright for web-based tracking links when needed
- Adds deliveries to Parcel app via API
- Moves processed emails to the Orders folder
- Handles Amazon emails specially (auto-sync to Parcel, but still organizes)
- Archives order confirmations to Orders folder
- Supports multiple email providers (Fastmail, Gmail, Outlook)

## Setup

Run the setup command to configure your providers:

```
/inbox-to-parcel:setup
```

## Usage

```
/inbox-to-parcel:track              # Process recent shipping emails
/inbox-to-parcel:track --days 14    # Look back 14 days
```

## Requirements

### MCP Servers

- **Email Provider** (one of):
  - `fastmail` - Fastmail MCP server
  - `gmail` - Gmail MCP server (via Smithery)
  - `outlook` - Outlook MCP server (via Smithery)

- **Package Tracking**:
  - `parcel-api-mcp` - Parcel app API
  - Install: `npx -y @smithery/cli@latest install @NOVA-3951/parcel-api-mcp --client claude`
  - Requires API key from: https://web.parcelapp.net/#apiPanel

- **Browser Automation**:
  - `playwright` - For web-based tracking extraction (bundled in plugin)

## Configuration

Provider settings are stored in `data/settings.yaml`. The setup command will configure this for you.

## Data Files

- `data/shipping-patterns.json` - Patterns for detecting shipping emails
- `data/settings.yaml` - Provider configuration

## How It Works

1. **Gets existing deliveries** from Parcel to avoid duplicates
2. **Scans inbox** for shipment notification emails (INBOX only)
3. **Extracts tracking info** from emails or web-based tracking links
4. **Adds new deliveries** to Parcel app via API
5. **Moves processed emails** to the Orders folder

## Supported Carriers

| Carrier | Code |
|---------|------|
| UPS | ups |
| FedEx | fedex |
| USPS | usps |
| DHL Express | dhl |
| DHL eCommerce | dhlecom |
| OnTrac | ont |
| LaserShip | laser |
| UPS Mail Innovations | upsmi |

## Special Handling

- **Amazon emails**: Skipped for Parcel (auto-syncs), but moved to Orders folder
- **Order confirmations**: Moved to Orders folder even without tracking numbers
- **Duplicates**: Automatically detected and skipped to preserve API rate limits

## Rate Limits

- Parcel API: 20 add requests per day
- Always checks for duplicates before adding to avoid wasting calls
