## Parcel API Initialization (Standard Pattern)

**Some agents need Parcel API access for package tracking.** The provider is configured in settings.yaml.

### Step 1: Check Settings

```
Read: ~/.claude/data/chief-of-staff/settings.yaml
```

Extract:
- `PARCEL_ENABLED` = `integrations.parcel` (boolean)
- `PARCEL_PROVIDER` = `providers.parcel.active` (e.g., "parcel-api")
- `PARCEL_TOOLS` = `providers.parcel.mappings[PARCEL_PROVIDER]`

**If `integrations.parcel` is `false`**, STOP and display:
```
Parcel integration is disabled in settings.yaml.

To enable: set integrations.parcel to true in ~/.claude/data/chief-of-staff/settings.yaml
```

### Step 2: Load Parcel Tools via ToolSearch

```
ToolSearch query: "+parcel"
```

This discovers the Parcel API MCP tools.

### Step 3: Verify Required Tools

Check that these tools were discovered:
- `get_deliveries` - Required for duplicate checking
- `add_delivery` - Required for adding new packages
- `get_supported_carriers` - Required for carrier code lookup

**If tools missing**, display:
```
Parcel API MCP not configured!

Install: npx -y @smithery/cli@latest install @NOVA-3951/parcel-api-mcp --client claude
Requires API key from: https://web.parcelapp.net/#apiPanel
```

### Step 4: Use Mapped Tool Names

Throughout the agent, reference tools via the mappings from settings.yaml:

**CORRECT** (use mapping):
```
Call PARCEL_TOOLS.get_deliveries with filter_mode: "active"
Call PARCEL_TOOLS.add_delivery with tracking_number, carrier
Call PARCEL_TOOLS.get_supported_carriers
```

**INCORRECT** (hardcoded):
```
Call mcp__parcel-api-mcp__get_deliveries  <- DON'T DO THIS
```

---

## Quick Reference: Parcel Tool Operations

| Operation | Description | Common Parameters |
|-----------|-------------|-------------------|
| `get_deliveries` | List deliveries | `filter_mode` ("active", "recent", "all") |
| `add_delivery` | Add new delivery | `tracking_number`, `carrier`, `description` |
| `get_supported_carriers` | List carrier codes | (none) |
| `get_delivery_status_codes` | Status code meanings | (none) |

**Rate Limits:**
- `add_delivery`: 20 requests per day
- `get_deliveries`: 20 requests per hour
