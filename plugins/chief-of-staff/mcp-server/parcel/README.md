# Parcel MCP Server

MCP server for interacting with the [Parcel](https://parcelapp.net/) delivery tracking app.

## Setup

### 1. Get your Parcel API Key

1. Open the Parcel app on your Mac
2. Go to **Settings > Integrations**
3. Enable API access
4. Copy your API key

### 2. Set Environment Variable

Add to your shell profile:

```bash
export PARCEL_API_KEY="your-api-key-here"
```

### 3. Build the Server

```bash
cd mcp-server/parcel
npm install
npm run build
```

## Tools

| Tool | Description |
|------|-------------|
| `get_deliveries` | Get active and recent deliveries with tracking status |
| `add_delivery` | Add a new tracking number to Parcel |
| `get_supported_carriers` | List supported carrier codes |
| `get_delivery_status_codes` | Reference for delivery status meanings |

## Carrier Codes

Common carriers:
- `ups` - UPS
- `fedex` - FedEx
- `usps` - USPS
- `dhl` - DHL
- `amazon` - Amazon Logistics
- `ontrac` - OnTrac
- `lasership` - LaserShip

Use `get_supported_carriers` for the full list.

## Usage

This MCP server is automatically configured when the chief-of-staff plugin is installed.

To test directly:

```bash
PARCEL_API_KEY=$PARCEL_API_KEY node dist/server.js
```

## Development

```bash
# Run with tsx for development
npm run dev

# Build for production
npm run build
```
