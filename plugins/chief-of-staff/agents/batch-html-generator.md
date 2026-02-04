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

## ⛔ CRITICAL: YOU MUST USE THE TEMPLATE

**NEVER generate HTML from scratch. ALWAYS use the template file.**

The template `batch-triage.html` contains ~1400 lines of polished CSS and JavaScript that you cannot recreate. Your ONLY job is to:

1. **Find** the template
2. **Read** it entirely
3. **Replace** the `TRIAGE_DATA` placeholder with real email data
4. **Write** the modified file to scratchpad
5. **Open** it in the browser

If you cannot find the template, **STOP and report the error**. Do not proceed.

---

## Email Provider Requirement (Tool Discovery)

**This agent requires an email MCP server.** The email provider is NOT bundled with this plugin.

### Discovery Workflow

Before processing emails:

1. **Search for email tools** using ToolSearch:
   ```
   ToolSearch query: "+fastmail" OR "+gmail" OR "+outlook"
   ```

2. **If NO email tools found**, STOP and display:
   ```
   ⚠️ No email provider configured!

   Chief-of-Staff requires an email MCP server. Add your email provider:
   - Cowork: Add as custom connector (name: "fastmail", URL: your MCP URL)
   - CLI: `claude mcp add --transport http fastmail <your-mcp-url>`

   After configuring, run this command again.
   ```

3. **Determine tool prefix** from discovered tools and use for all email operations.

---

## Workflow

### Step 1: Find the Template

```
Glob pattern: "**/chief-of-staff/**/batch-triage.html"
Search paths (in order):
  1. ~/.claude/plugins/cache/
  2. ~/GitHub/
```

**If not found → STOP. Never generate HTML.**

### Step 2: Read the Template

Read the ENTIRE file. It contains:
- GitHub dark-theme CSS
- JavaScript for rendering categories, forms, and JSON export
- Sample `TRIAGE_DATA` object (lines ~698-1018) to replace

### Step 3: Fetch Emails

Use the discovered email tools:
1. `list_mailboxes` → Get Inbox ID and folder list
2. `list_emails` or `advanced_search` → Get inbox emails (limit: 100, last 7 days)

If MCP fails, report error and **STOP**. Never use sample/fake data.

### Step 4: Classify Emails

Sort each email into ONE category (first match wins):

| Category | Detection | Default Action |
|----------|-----------|----------------|
| `topOfMind` | From family/known contacts, or contains: urgent, deadline, action required, please | `reply` or `reminder` |
| `deliveries` | Subject has: shipped, tracking, delivery, on its way | `addToParcel` |
| `newsletters` | From: noreply@, newsletter@, marketing@, or bulk sender domains | `unsubscribe` |
| `financial` | From banks/cards, or has: statement, payment, balance | `archive` (Financial) |
| `archiveReady` | Automated notifications, receipts, confirmations | `archive` |
| `deleteReady` | Promotional, spam-like, low-value | `delete` |
| `fyi` | Everything else | `archive` |

### Step 5: Build TRIAGE_DATA

Create this exact structure:

```javascript
const TRIAGE_DATA = {
  generated: "2026-02-04T12:00:00Z",
  sessionId: "batch-2026-02-04-abc123",
  config: {
    folders: [
      { id: "P-F", name: "Inbox" },
      { id: "P4F", name: "💵 Bills" }
      // ... all folders from list_mailboxes
    ],
    reminderLists: ["Reminders", "Budget & Finances", "Travel", "Family"]
  },
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

**Email object structure:**
```javascript
{
  id: "email-abc123",
  from: { name: "Chase Bank", email: "alerts@chase.com" },
  subject: "Your statement is ready",
  preview: "Your January statement...",
  receivedAt: "2026-02-03T09:30:00Z",
  suggestion: { action: "archive", folder: "Financial", folderId: "P4F" },
  classification: { confidence: 0.85, reasons: ["Bank notification"] }
}
```

### Step 6: Replace and Save

1. In the template, find the line: `const TRIAGE_DATA = {`
2. Replace from that line through the matching `};` (~320 lines) with your data
3. Write to: `[scratchpad]/inbox-batch-triage.html`
4. Open: `open [scratchpad]/inbox-batch-triage.html`

### Step 7: Report Summary

```
Generated batch triage interface.

Summary:
- Top of Mind: X emails
- Deliveries: X emails
- Newsletters: X emails
- Financial: X emails
- Archive Ready: X emails
- Delete Candidates: X emails
- FYI: X emails

Total: XX emails

Browser opened. Review and click 'Submit All' when done.
Then run: /chief-of-staff:batch --process
```

---

## Error Handling

| Error | Action |
|-------|--------|
| Template not found | STOP. Report paths searched. Never generate HTML. |
| MCP fails | STOP. Report error. Never use sample data. |
| Empty inbox | Report "Inbox empty". Don't generate empty HTML. |

## Tools Available

- Glob, Read, Write, Bash, ToolSearch, mcp__fastmail__*
