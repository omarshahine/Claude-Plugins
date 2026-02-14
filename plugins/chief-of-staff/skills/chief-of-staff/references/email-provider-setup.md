# Email Provider Setup Reference

Chief-of-Staff does NOT bundle an email MCP server. Users must configure their email provider separately.

## Why Separate Configuration?

1. **Privacy**: Your email MCP URL is personal - it shouldn't be in a public plugin
2. **Flexibility**: Works with any email provider (Fastmail, Gmail, Outlook)
3. **Cowork compatibility**: Environment variables don't work in Cowork

## Supported Providers

| Provider | Recommended | Notes |
|----------|-------------|-------|
| Fastmail | Yes | Full MCP API support, advanced search |
| Gmail | Supported | Requires Gmail MCP server |
| Outlook | Supported | Requires Microsoft Graph MCP |

## Setup Instructions

### Option A: Cowork (Web Interface)

1. Open Cowork settings
2. Add a **Custom Connector**:
   - **Name**: `fastmail` (or `gmail`, `outlook`)
   - **URL**: Your email MCP server URL
3. Restart your session

### Option B: Claude Code CLI

```bash
# Fastmail
claude mcp add --transport http fastmail <your-fastmail-mcp-url>

# Gmail
claude mcp add --transport http gmail <your-gmail-mcp-url>

# Outlook
claude mcp add --transport http outlook <your-outlook-mcp-url>
```

## Verification

After setup, run `/chief-of-staff:setup` to verify the connection:
- It will discover your email provider automatically
- Test the connection
- Configure folder mappings

## Troubleshooting

**"No email provider configured" error:**
1. Check that your email MCP is added (Cowork settings or `claude mcp list`)
2. Verify the URL is correct
3. Restart Claude Code/Cowork session

**Connection failures:**
1. Check `/mcp` to see server status
2. Re-authenticate if needed (OAuth providers)
3. Verify your MCP server is running
