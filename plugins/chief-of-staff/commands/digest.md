---
description: Generate a summary of automated emails
argument-hint: "[--all]"
---

# /chief-of-staff:digest

Generate a categorized digest of your automated emails, highlighting items that need attention.

## Usage

```
/chief-of-staff:digest         # Summarize unread automated emails
/chief-of-staff:digest --all   # Include last 24 hours regardless of read status
```

## Arguments

- **--all**: Include all emails from last 24 hours, not just unread

## What It Does

1. **Fetches** unread emails from the automated folder (or last 24h with --all)
2. **Categorizes** by priority and type
3. **Generates** a scannable digest
4. **Offers bulk actions** via AskUserQuestion

## Categories

**Priority (shown first):**
- Security Alerts: sign-in, new device, password, 2FA
- Payment Issues: declined, failed, billing errors
- Account Issues: verify, confirm, action required

**Standard:**
- Social: LinkedIn, Twitter notifications
- Marketing: promotions, sales
- Notifications: GitHub, app updates
- Receipts: order confirmations

## Example Output

```markdown
# Automated Email Digest - Feb 2, 2026

## Needs Attention (3 emails)

### Security Alerts
- **Google**: New sign-in from Windows in Seattle
  → Review activity: [link]

### Payment Issues
- **Netflix**: Payment failed for February
  → Update payment method: [link]

## Social (8 emails)
- LinkedIn: 3 connection requests, 2 profile views
- Twitter: 3 mentions

## Marketing (12 emails)
- Amazon: 4 promotional emails
- Various retailers: 8 sale notifications

## Receipts (2 emails)
- Uber: Receipt for trip on Feb 1 ($24.50)
- DoorDash: Receipt for order Feb 1 ($35.67)

---
Summary: 25 emails | 3 need attention | 22 routine

Actions:
1. Mark marketing as read
2. Archive receipts
3. Mark all as read
```

## Implementation

Use the Task tool to invoke the digest-generator agent:

```
subagent_type: "chief-of-staff:digest-generator"
prompt: "Generate a digest of automated emails. [Include all from last 24h if --all flag]"
```
