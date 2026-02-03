---
description: Visual HTML batch triage interface
argument-hint: "[--generate | --process | --retry]"
---

# /chief-of-staff:batch

Generate or process a visual HTML batch triage interface.

## Usage

```
/chief-of-staff:batch              # Generate HTML interface
/chief-of-staff:batch --generate   # Same as above
/chief-of-staff:batch --process    # Process downloaded decisions
/chief-of-staff:batch --retry      # Retry failed items from last batch
```

## Arguments

- **--generate** (default): Create the HTML batch triage page
- **--process**: Process decisions from downloaded JSON file
- **--retry**: Retry only failed items from previous batch
- **--days N**: Override lookback period (default: 7)
- **--limit N**: Override email limit (default: 100)

## Workflow

### Generate Mode

1. Fetches inbox emails from last 7 days
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

**Generate Mode:**
```
subagent_type: "chief-of-staff:batch-html-generator"
prompt: "Generate the HTML batch triage interface. Look back [days] days, limit [N] emails."
```

**Process Mode:**
```
subagent_type: "chief-of-staff:batch-processor"
prompt: "Process batch triage decisions from the downloaded JSON file."
```

**Retry Mode:**
```
subagent_type: "chief-of-staff:batch-processor"
prompt: "Retry failed items from the previous batch. Read failures from batch-state.yaml."
```
