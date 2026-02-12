---
description: Visual HTML batch triage interface
argument-hint: "[--generate | --process | --retry | --reset | --full]"
---

# /chief-of-staff:batch

Generate or process a visual HTML batch triage interface.

## Usage

```
/chief-of-staff:batch              # Generate HTML interface (incremental if state exists)
/chief-of-staff:batch --generate   # Same as above
/chief-of-staff:batch --process    # Process downloaded decisions
/chief-of-staff:batch --retry      # Retry failed items from last batch
/chief-of-staff:batch --reset      # Clear sync state, full fetch
/chief-of-staff:batch --full       # One-time full fetch, save new state
```

## Arguments

- **--generate** (default): Create the HTML batch triage page
- **--process**: Process decisions from downloaded JSON file
- **--retry**: Retry only failed items from previous batch
- **--reset**: Clear sync state completely, do full fetch (starts fresh)
- **--full**: One-time full fetch but save new state for future incremental calls
- **--days N**: Override lookback period (default: 7)
- **--limit N**: Override email limit (default: 100)

## Workflow

### Generate Mode

1. **Incremental sync**: Fetches only NEW inbox emails since last triage (or all on first run)
   - Uses JMAP `queryChanges` for Fastmail; falls back to `list_emails` for other providers
   - `--reset` clears state and re-fetches everything
   - `--full` does a one-time full fetch but saves state for next time
2. Classifies into categories (Top of Mind, Deliveries, Newsletters, etc.)
3. Generates standalone HTML file with embedded data
4. Opens in browser for review

**HTML Interface Features:**
- Emails grouped by category
- Default actions pre-selected
- Dropdown to change action
- Text field for steering notes
- "Submit All" downloads decisions JSON

### Process Mode

1. Finds decisions JSON (Downloads folder or scratchpad)
2. Groups decisions by action type
3. Executes inline actions (archive, delete, keep)
4. Delegates batch actions to sub-agents (parcel, newsletter, reminder)
5. Reports summary with success/failure counts

## Example Output

### Generate Mode

```
Generated batch triage interface.

Summary:
- Top of Mind: 3 emails
- Deliveries: 5 emails
- Newsletters: 8 emails
- Financial: 4 emails
- Archive Ready: 6 emails
- Delete Candidates: 2 emails
- FYI: 12 emails

Total: 40 emails

Browser opened. Review emails, adjust actions, click 'Submit All'.

After submitting, run: /chief-of-staff:batch --process
```

### Process Mode

```
Processing 40 decisions from batch-2026-02-02-abc123...

INLINE ACTIONS
--------------
Archive: 15 emails
  - 8 to Financial
  - 5 to Orders
  - 2 to Travel
Delete: 5 emails
Keep: 2 emails (flagged)

DELEGATED BATCHES
-----------------
Parcel: 5 packages → Added to Parcel
Newsletters: 8 → Unsubscribed from 6, 2 failed
Reminders: 3 → Created in Apple Reminders
Calendar: 2 → Created events

SUMMARY
-------
Total: 40 decisions
Successful: 38
Failed: 2

Failed items saved for retry.
```

## Implementation

**CRITICAL**: This command MUST delegate to sub-agents via the Task tool. Do NOT attempt to perform actions directly in this command.

**Generate Mode (default or --generate):**
```
Use the Task tool with:
  subagent_type: "chief-of-staff:batch-html-generator"
  prompt: |
    Generate the HTML batch triage interface.
    Parameters:
    - Look back: [days] days (default: 7)
    - Limit: [N] emails (default: 100)
    - Sync mode: [--reset | --full | (default: incremental if state exists)]

    If --reset was passed: Clear sync-state.yaml before fetching. Full re-fetch.
    If --full was passed: Do full fetch this time, save new state for future incremental.
    Otherwise: Use incremental sync if sync-state.yaml has query_state.

    IMPORTANT: If email MCP fails, report the error immediately.
    Do NOT generate sample data or placeholder HTML.
```

**Process Mode (--process):**
```
Use the Task tool with:
  subagent_type: "chief-of-staff:batch-processor"
  prompt: |
    Process batch triage decisions from the downloaded JSON file.

    Check these locations for the decisions file:
    1. ~/Downloads/inbox-triage-decisions-*.json
    2. Scratchpad directory

    IMPORTANT:
    - Check steering text for reply intent even if action is not "reply"
    - Use reply_to_email with markdownBody for drafts
    - Initialize data files from .example templates if missing
    - Record all decisions to decision-history.yaml for learning
```

**Retry Mode (--retry):**
```
Use the Task tool with:
  subagent_type: "chief-of-staff:batch-processor"
  prompt: |
    Retry failed items from the previous batch.
    Read failures from ~/.claude/data/chief-of-staff/batch-state.yaml and reprocess only those items.
```

**Why Task tool is required:**
- Sub-agents have specialized tools and prompts
- Direct execution would miss important context (patterns, rules, MCP setup)
- Learning system expects consistent agent behavior
