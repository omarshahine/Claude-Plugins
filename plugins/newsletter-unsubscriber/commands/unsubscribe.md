---
description: Scan inbox for newsletters and help unsubscribe from unwanted ones
---

# /newsletter-unsubscriber:unsubscribe

Scan your inbox for newsletters and help you unsubscribe from the ones you no longer want.

## Usage

```
/newsletter-unsubscriber:unsubscribe
```

## What It Does

1. **Loads your lists** - Reads allowlist and previously unsubscribed senders
2. **Scans inbox** for newsletters (skips allowlisted senders)
3. **Flags repeat offenders** - Highlights senders who ignored previous unsubscribes
4. **Groups newsletters** by sender domain with frequency counts
5. **Asks which to unsubscribe** - You select which newsletters to remove
6. **Confirms your selection** before taking action
7. **Executes unsubscribes** via mailto or web forms
8. **Asks about allowlist** - Offers to add skipped newsletters to allowlist
9. **Updates your lists** - Tracks unsubscribed senders + allowlist additions
10. **Organizes emails** by moving them to Newsletters/Unsubscribed folder

## Newsletter Detection

Uses RFC 2369 email headers to precisely identify newsletters:
- **`List-Unsubscribe`** - The definitive newsletter/mailing list indicator
- **`List-Id`** - Identifies mailing lists

This is far more accurate than guessing from subject lines. Gmail and Yahoo require these headers for marketing emails since June 2024.

## Allowlist & Repeat Offender Tracking

The agent maintains two lists in `data/newsletter-lists.yaml`:

| List | Purpose |
|------|---------|
| **Allowlist** | Newsletters you want to keep - skipped in future scans |
| **Unsubscribed** | Senders you've unsubscribed from - used to detect repeat offenders |

**Repeat offenders** are senders who continue emailing after you unsubscribed. These are flagged in the selection list so you can take action.

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
| Complex flow | Reports failure with URL |

## Example Output

```
Newsletter Unsubscribe Summary
==============================

REPEAT OFFENDERS (1):
- spammy.com - Unsubscribed 2025-12-01, sent 3 more emails!
  -> Unsubscribed again via web form

Successfully unsubscribed (3):
- marketing-company.com (12 emails) - via web form
- news-digest.com (10 emails) - via mailto
- tech-updates.io (8 emails) - via web form

Failed to unsubscribe (1):
- protected-site.com (3 emails) - CAPTCHA required
  Manual URL: https://protected-site.com/unsubscribe?token=xxx

Added to allowlist (2):
- stratechery.com - Will skip in future scans
- join1440.com - Will skip in future scans

Lists updated: newsletter-lists.yaml
Emails organized: 28 emails moved to Newsletters/Unsubscribed folder
```

## Implementation

This command uses a two-phase workflow:

### Phase 1: Scan (agent returns data)
```
subagent_type: "newsletter-unsubscriber:newsletter-unsubscriber"
prompt: "Scan inbox for newsletters. Return the structured list - do not use AskUserQuestion."
```

### Phase 2: User Selection (parent handles)
The parent agent uses AskUserQuestion to present newsletters and get user selections.

### Phase 3: Execute (agent performs actions)
```
subagent_type: "newsletter-unsubscriber:newsletter-unsubscriber"
prompt: "Execute these actions:
- UNSUBSCRIBE: domain1.com (url: https://example.com/unsubscribe?id=123, emailIds: [msg1, msg2])
- UNSUBSCRIBE: domain2.com (url: https://other.com/unsub, emailIds: [msg3])
- ALLOWLIST: domain3.com, domain4.com
Then update newsletter-lists.local.yaml and move emails to Unsubscribed folder."
```
