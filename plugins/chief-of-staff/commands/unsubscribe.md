---
description: Scan inbox for newsletters and help unsubscribe from unwanted ones
---

# /chief-of-staff:unsubscribe

Scan your inbox for newsletters and marketing emails, then help you unsubscribe from the ones you don't want.

## Usage

```
/chief-of-staff:unsubscribe          # Scan and present newsletters for selection
```

## What It Does

1. **Scans inbox** for emails with List-Unsubscribe headers (RFC 2369)
2. **Groups by sender** with frequency counts
3. **Identifies repeat offenders** (senders you've unsubscribed from before)
4. **Skips allowlisted** newsletters you want to keep
5. **Presents options** for selection
6. **Executes unsubscribes** via web form (Playwright) or mailto
7. **Moves processed emails** to Unsubscribed folder

## Newsletter Detection

Detected via RFC headers:
- `List-Unsubscribe` - Required by Gmail/Yahoo for marketing since June 2024
- `List-Id` - Standard mailing list identifier
- `List-Unsubscribe-Post` - One-click unsubscribe capable

Plus common patterns:
- Sender patterns: noreply@, newsletter@, digest@, marketing@
- Subject keywords: newsletter, weekly, monthly, digest, roundup

## Example Output

```
Newsletters Found
=================

Found 8 newsletters in your inbox:

REPEAT OFFENDERS (1):
- spammy-deals.com (5 emails) - Unsubscribed 2025-11-15, still sending!

MARKETING NEWSLETTERS (5):
1. Example Newsletter (example.com) - 12 emails
2. Tech Digest (techsite.com) - 8 emails
3. Daily Deals (deals.example.com) - 15 emails
4. Product Updates (saas-company.com) - 6 emails
5. Weekly Roundup (news.example.com) - 4 emails

ALREADY ALLOWLISTED (2):
- example-newsletter.com (keeping)
- example-blog.net (keeping)

Which ones would you like to unsubscribe from?
```

## Implementation

Use the Task tool to invoke the newsletter-unsubscriber agent:

```
subagent_type: "chief-of-staff:newsletter-unsubscriber"
prompt: "Scan inbox for newsletters and present options for unsubscribing. Show allowlisted newsletters and repeat offenders."
```
