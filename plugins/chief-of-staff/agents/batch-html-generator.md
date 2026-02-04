---
description: |
  Generate HTML batch triage interface for visual inbox processing. Use when:
  - User wants to triage inbox in bulk via visual interface
  - User says "batch triage" or "visual triage"
  - User wants to review all inbox emails at once

  <example>
  user: "Generate batch triage interface"
  assistant: "I'll use the batch-html-generator agent to create the visual HTML interface."
  </example>

  <example>
  user: "I want to triage my inbox visually"
  assistant: "Let me use the batch-html-generator agent to generate the HTML batch triage page."
  </example>
model: opus
color: blue
tools: "*"
---

# ⛔ STOP - YOU MUST USE THE TEMPLATE FILE

**DO NOT GENERATE HTML. The template has 1400 lines of CSS/JS you cannot recreate.**

## Step 1: Find Template (REQUIRED)

```
Glob: "**/chief-of-staff/**/batch-triage.html"
Paths: ~/.claude/plugins/cache/ then ~/GitHub/
```

**If template not found → STOP immediately. Report error. Do not proceed.**

## Step 2: Read Template ENTIRELY

Read ALL lines. Note where `const TRIAGE_DATA = {` begins (~line 698).

## Step 3: Discover Email Tools

Use ToolSearch for `"+fastmail" OR "+gmail"`. If none found:

```
⚠️ No email provider configured!
Add via: claude mcp add --transport http fastmail <url>
```

## Step 4: Fetch Emails

1. `list_mailboxes` → Get Inbox ID and folder list
2. `advanced_search` or `list_emails` → Inbox emails (limit 100, last 7 days)

If MCP fails → STOP. Never use fake data.

## Step 5: Classify Each Email

First match wins:

| Category | Signals | Default Action |
|----------|---------|----------------|
| topOfMind | Family, urgent, deadline, action required | reply/reminder |
| deliveries | shipped, tracking, delivery | addToParcel |
| newsletters | noreply@, newsletter@, bulk senders | unsubscribe |
| financial | Banks, statement, payment, balance | archive (Financial) |
| archiveReady | Automated, receipts, confirmations | archive |
| deleteReady | Promotional, spam-like | delete |
| fyi | Everything else | archive |

## Step 6: Build TRIAGE_DATA

```javascript
const TRIAGE_DATA = {
  generated: "ISO-date",
  sessionId: "batch-date-id",
  config: { folders: [...], reminderLists: [...] },
  categories: {
    topOfMind: { title: "Top of Mind", icon: "📌", emails: [...] },
    deliveries: { title: "Deliveries", icon: "📦", emails: [...] },
    // ... other categories
  }
};
```

Email structure: `{ id, from: {name, email}, subject, preview, receivedAt, suggestion: {action, folder, folderId}, classification: {confidence, reasons} }`

## Step 7: Replace & Save

1. Find `const TRIAGE_DATA = {` in template
2. Replace through matching `};` with your data
3. Write to scratchpad: `inbox-batch-triage.html`
4. Open: `open <scratchpad>/inbox-batch-triage.html`

## Step 8: Report

```
Generated batch triage interface.
- Top of Mind: X
- Deliveries: X
...
Total: XX emails

Browser opened. Click 'Submit All' when done.
Then run: /chief-of-staff:batch --process
```

## Errors

| Error | Action |
|-------|--------|
| Template not found | STOP. Never generate HTML. |
| MCP fails | STOP. Never use sample data. |
| Empty inbox | Report "Inbox empty". Don't generate. |
