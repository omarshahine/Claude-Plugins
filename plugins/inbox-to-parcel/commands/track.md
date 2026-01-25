---
description: Process shipping emails and add tracking to Parcel app
---

# /inbox-to-parcel:track

Process shipping notification emails from your inbox and add tracking numbers to the Parcel app.

## Usage

```
/inbox-to-parcel:track              # Process recent shipping emails
/inbox-to-parcel:track --days 14    # Look back 14 days
```

## Arguments

- **--days N**: Number of days to look back (default: 7)

## What It Does

1. **Gets existing deliveries** from Parcel to avoid duplicates
2. **Scans inbox** for shipment notification emails (INBOX only, not archived)
3. **Extracts tracking info** from emails or uses Playwright for web-based tracking links
4. **Adds new deliveries** to Parcel app via API
5. **Moves processed emails** to the Orders folder

## Supported Carriers

| Carrier | Code |
|---------|------|
| UPS | ups |
| FedEx | fedex |
| USPS | usps |
| DHL | dhl |
| OnTrac | ont |
| LaserShip | laser |

## Special Handling

- **Amazon emails**: Skipped for Parcel (auto-syncs), but still moved to Orders folder
- **Order confirmations**: Moved to Orders folder even without tracking numbers
- **Duplicates**: Automatically detected and skipped to preserve API rate limits

## Example Output

```
Order Tracking Summary
======================

Scanned: 15 emails from inbox

Added to Parcel (3 new):
- 1Z999AA10123456784 (UPS) - B&H Photo
- 794644790138 (FedEx) - REI
- 9400111899223456789012 (USPS) - Etsy

Already in Parcel (2 skipped):
- 1Z999AA10987654321 (UPS)
- 92612999999999999999999 (USPS)

Moved to Orders folder: 8 emails
- 3 shipping notifications
- 5 order confirmations
```

## Implementation

Use the Task tool to invoke the inbox-to-parcel agent:

```
subagent_type: "inbox-to-parcel:inbox-to-parcel"
prompt: "Process shipping emails from inbox and add tracking to Parcel. Look back [days] days."
```
