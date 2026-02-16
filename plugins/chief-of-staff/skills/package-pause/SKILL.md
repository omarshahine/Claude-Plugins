---
name: package-pause
description: |
  Carrier vacation hold knowledge base for USPS, UPS, and FedEx. Use when:
  - User says "pause packages", "hold packages", or "vacation hold"
  - User asks about pausing deliveries before a trip
  - User mentions "hold my mail" or "stop deliveries"
  - User asks about USPS hold mail, UPS My Choice, or FedEx Delivery Manager vacation holds
---

# Package Pause — Vacation Delivery Hold Knowledge

Automate setting vacation holds across USPS, UPS, and FedEx before trips. Uses Playwright browser automation to fill out each carrier's vacation hold form.

## Carrier Comparison

| Carrier | Service Name | Max Hold | Cost | URL |
|---------|-------------|----------|------|-----|
| USPS | Hold Mail | 30 days | Free | https://www.usps.com/manage/hold-mail.htm |
| UPS | My Choice Vacation Hold | 14 days | Free | https://wwwapps.ups.com/ppc/ppc.html?loc=en_US#/preferencePage/mychoicePreference |
| FedEx | Delivery Manager Vacation Hold | 14 days | Free | https://www.fedex.com/apps/myprofile/deliverymanager/ |

## Carrier Details

### USPS Hold Mail

- **Duration**: 3–30 days
- **Deadline**: Must be submitted by 3:00 AM ET on the start date
- **Delivery on resume**: All held mail delivered on the day after the hold ends, or you can pick up at the post office
- **Account required**: USPS.com account with verified address
- **Packages covered**: All USPS mail and packages (First Class, Priority, Media Mail, etc.)
- **URL**: `https://www.usps.com/manage/hold-mail.htm`

### UPS My Choice Vacation Hold

- **Duration**: Up to 14 days
- **Gap requirement**: 6-day gap required between consecutive holds
- **Account required**: UPS My Choice membership (free tier works)
- **Packages covered**: UPS Ground, UPS Air (Express + Ground)
- **Process**: Enter dates → click "Update My Delivery Options" → set preferred delivery date → click yellow "Update" button at bottom
- **URL**: `https://wwwapps.ups.com/ppc/ppc.html?loc=en_US#/preferencePage/mychoicePreference`
- **Login URL**: `https://www.ups.com/lasso/login?returnto=https%3a//wwwapps.ups.com/ppc/ppc.html%3floc%3den_US&reasonCode=-1#/preferencePage/mychoicePreference`

### FedEx Delivery Manager Vacation Hold

- **Duration**: Up to 14 days
- **Account required**: FedEx Delivery Manager account (free)
- **Packages covered**: FedEx Express and FedEx Ground only (not FedEx Freight)
- **Process**: Set start and end dates in the Vacation Hold section
- **URL**: `https://www.fedex.com/apps/myprofile/deliverymanager/?locale=en_US&cntry_code=us&wpro=true`

## Duration Validation

When the user provides dates:
- If duration is **1–14 days**: All three carriers can accommodate
- If duration is **15–30 days**: Only USPS can hold that long; warn that UPS and FedEx max out at 14 days
- If duration is **>30 days**: No carrier supports holds this long; suggest alternative arrangements

## Processing Order

Process carriers in this order:
1. **USPS** first — strictest deadline (3 AM ET cutoff)
2. **UPS** second — most complex form (multi-step)
3. **FedEx** last — simplest form

## Related Command

Use `/chief-of-staff:package-pause` to invoke the automation, or ask "pause my packages" / "set vacation holds".
