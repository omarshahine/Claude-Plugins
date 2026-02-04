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
model: sonnet
color: blue
tools: "*"
---

# Batch HTML Generator

Generate an HTML batch triage interface for visual inbox processing.

## Step 1: Discover Email Tools

Use ToolSearch to find and load Fastmail MCP tools:
```
ToolSearch query: "+fastmail mailbox"
```

If no email tools found, STOP and display:
```
⚠️ No email provider configured!

Chief-of-Staff requires the Fastmail MCP server. Configure it via:
- CLI: `claude mcp add --transport http fastmail <your-mcp-url>`

After configuring, restart Claude Code and run this command again.
```

## Step 2: Fetch Mailboxes and Emails

1. Call `mcp__fastmail__list_mailboxes` to get folder structure
2. Find the Inbox mailbox (role: "inbox" or name: "Inbox")
3. Call `mcp__fastmail__list_emails` with:
   - mailboxId: inbox ID
   - limit: from prompt parameters (default: 100)

## Step 3: Find Template (REQUIRED)

```
Glob: "**/chief-of-staff/**/batch-triage.html"
Paths: ~/.claude/plugins/cache/ then ~/GitHub/
```

**If not found → STOP. Report error. Never generate HTML from scratch.**

## Step 4: Read Template

Read the entire file. Find `const TRIAGE_DATA = {` (~line 698).

## Step 5: Classify Emails

Classify each email from step 2 into ONE category (first match wins):

| Category | Signals | Default Action |
|----------|---------|----------------|
| topOfMind | Family, urgent, deadline, action required | reply/reminder |
| deliveries | shipped, tracking, delivery | addToParcel |
| newsletters | noreply@, newsletter@, $canunsubscribe | unsubscribe |
| financial | Banks, statement, payment, balance | archive (Financial) |
| archiveReady | Automated, receipts, CC'd emails | archive |
| deleteReady | Promotional, spam-like, old tutorials | delete |
| fyi | Everything else | archive |

## Step 6: Build TRIAGE_DATA

```javascript
const TRIAGE_DATA = {
  generated: "ISO-date",
  sessionId: "batch-YYYY-MM-DD-id",
  config: { folders: [...from input...], reminderLists: ["Reminders", "Budget & Finances", "Travel", "Family"] },
  categories: {
    topOfMind: { title: "Top of Mind", icon: "📌", emails: [...] },
    deliveries: { title: "Deliveries", icon: "📦", emails: [...] },
    newsletters: { title: "Newsletters", icon: "📰", emails: [...] },
    financial: { title: "Financial", icon: "💰", emails: [...] },
    archiveReady: { title: "Archive Ready", icon: "📁", emails: [...] },
    deleteReady: { title: "Delete Candidates", icon: "🗑️", emails: [...] },
    fyi: { title: "FYI", icon: "ℹ️", emails: [...] }
  }
};
```

Email structure: `{ id, from: {name, email}, subject, preview, receivedAt, suggestion: {action, folder?, folderId?}, classification: {confidence, reasons} }`

Use the folders from step 2 for the config.folders array.

## Step 7: Replace & Save

1. Find `const TRIAGE_DATA = {` in template (line 698)
2. Replace through line 970 (`};`) with your generated data
3. Write to scratchpad: `inbox-batch-triage.html`
4. Open: `open <scratchpad>/inbox-batch-triage.html`

## Step 8: Report

```
Generated batch triage interface.
- Top of Mind: X
- Deliveries: X
- Newsletters: X
- Financial: X
- Archive Ready: X
- Delete Candidates: X
- FYI: X
Total: XX emails

Browser opened. Click 'Submit All' when done.
Then run: /chief-of-staff:batch --process
```

## Errors

| Error | Action |
|-------|--------|
| No email MCP tools | STOP. Report configuration instructions. |
| Template not found | STOP. Report paths searched. |
| No emails in inbox | Report "No emails found in the last N days". |
