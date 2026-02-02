---
description: Visual HTML batch triage interface for bulk inbox processing
argument-hint: "[--process | --days N | --retry | --file PATH]"
---

# /inbox-triage:batch

Visual batch triage interface that lets you review and process all inbox emails at once through an HTML page.

## Usage

```
/inbox-triage:batch              # Generate HTML triage interface
/inbox-triage:batch --process    # Process submitted decisions
/inbox-triage:batch --days 14    # Generate with 14-day lookback
/inbox-triage:batch --retry      # Retry failed items from last run
/inbox-triage:batch --file PATH  # Process specific decisions file
```

## How It Works

### Step 1: Generate Interface

Run `/inbox-triage:batch` to:
1. Fetch inbox emails (last 7 days by default)
2. Classify emails into categories
3. Generate HTML with suggested actions
4. Open in your browser

### Step 2: Review in Browser

The HTML interface shows emails grouped by category:
- **Top of Mind** - Action items needing response
- **Deliveries** - Package shipments
- **Newsletters** - Marketing emails
- **Financial** - Banking/financial alerts
- **Archive Ready** - High-confidence filing matches
- **Delete Candidates** - Likely deletable
- **FYI** - Everything else

For each email:
- Review the suggested action
- Change action if needed (dropdown)
- Select archive folder if archiving
- Add steering text for context

### Step 3: Submit Decisions

Click "Submit All" to download a decisions JSON file.

### Step 4: Process Decisions

Run `/inbox-triage:batch --process` to:
1. Execute archive/delete/keep actions
2. Delegate packages to Parcel
3. Process newsletter unsubscribes
4. Create reminders
5. Report summary

## Categories and Default Actions

| Category | Default Action | When |
|----------|---------------|------|
| Top of Mind | Create Reminder | Action keywords detected |
| Deliveries | Add to Parcel | Shipping patterns match |
| Newsletters | Delete + Unsubscribe | Newsletter indicators |
| Financial | Archive to Financial | Banking domains/keywords |
| Archive Ready | Archive to [folder] | High-confidence filing match |
| Delete Candidates | Delete | Delete patterns match |
| FYI | Archive | No urgency detected |

## Available Actions

| Action | Description |
|--------|-------------|
| Archive | Move to specified folder |
| Delete | Delete permanently |
| Keep | Keep in inbox (optionally flag) |
| Reminder | Create Apple Reminder |
| Calendar | Create calendar event |
| Reply | Draft a reply |
| Add to Parcel | Track package + archive to Orders |
| Unsubscribe | Unsubscribe + delete |

## Implementation

### Generate HTML (default)

```
subagent_type: "inbox-triage:batch-html-generator"
prompt: "Generate the batch triage HTML interface. Fetch inbox emails from the last 7 days, classify them into categories, and create the HTML page. Open in browser when done."
```

With `--days N`:
```
prompt: "Generate the batch triage HTML interface. Fetch inbox emails from the last [N] days..."
```

### Process Decisions (`--process`)

```
subagent_type: "inbox-triage:batch-processor"
prompt: "Process the batch triage decisions. Find the most recent decisions JSON file, execute all actions, and report summary."
```

### Retry Failures (`--retry`)

```
subagent_type: "inbox-triage:batch-processor"
prompt: "Retry failed items from the previous batch triage run. Read batch-state.yaml, extract failures, and reprocess only those items."
```

### Process Specific File (`--file PATH`)

```
subagent_type: "inbox-triage:batch-processor"
prompt: "Process batch triage decisions from the specified file: [PATH]"
```

## Prerequisites

1. Run `/inbox-triage:setup` to configure email provider
2. Optionally run `/inbox-triage:learn` to improve classification

## Example Session

```
> /inbox-triage:batch

Generated batch triage interface.

Summary:
- Top of Mind: 3 emails
- Deliveries: 5 emails
- Newsletters: 8 emails
- Financial: 4 emails
- FYI: 12 emails

Total: 32 emails

Browser opened. Review emails, adjust actions, click 'Submit All'.

> [User reviews in browser, submits decisions]

> /inbox-triage:batch --process

Processing 32 decisions...

Archive: 10 emails archived
Delete: 4 emails deleted
Parcel: 5 packages added
Newsletters: 8 unsubscribed
Reminders: 3 created
Calendar: 1 event created
Keep: 1 email kept

All 32 decisions processed successfully.
```

## Files

- HTML: `[scratchpad]/inbox-triage-batch-YYYY-MM-DD.html`
- Decisions: `~/Downloads/inbox-triage-decisions-YYYY-MM-DD.json`
- State: `[data-dir]/batch-state.yaml`

## Comparison: Batch vs Interview Mode

| Aspect | Batch Mode (`/batch`) | Interview Mode (`/interview`) |
|--------|----------------------|------------------------------|
| Interface | Visual HTML in browser | Terminal conversation |
| Review | All at once | One by one |
| Speed | Fast bulk review | Slower, thorough |
| Best for | Desktop, visual review | Voice, hands-free |
| Shared | Same classification logic, same sub-agents |
