## Incremental Inbox Fetch (Standard Pattern)

**Purpose:** Fetch only NEW inbox emails since the last triage session, avoiding re-presenting emails the user already triaged.

### How It Works

1. **Read sync state** from `~/.claude/data/chief-of-staff/sync-state.yaml`
2. **Check capabilities** — does `EMAIL_TOOLS.get_inbox_updates` exist (not null)?
3. **Fetch emails** using the appropriate path:
   - **Incremental**: state exists + tool available + not `--reset`/`--full` → call with `sinceQueryState`
   - **Full query**: no state OR `--full` flag → call without `sinceQueryState`
   - **Fallback**: tool unavailable (non-Fastmail) → use `EMAIL_TOOLS.list_emails`
4. **Filter out** `seen_email_ids` from results (emails that stayed in inbox from previous sessions)
5. **Reconcile**: cross-check incremental results against a full inbox listing to catch orphaned emails
6. **After triage**: save new state and update `seen_email_ids`

### Step-by-Step Implementation

#### Before Fetching Emails

```
1. Read ~/.claude/data/chief-of-staff/sync-state.yaml
   - If file doesn't exist, initialize from sync-state.example.yaml or use defaults:
     query_state: null, last_sync: null, mailbox_id: null, seen_email_ids: []

2. Check if incremental sync is available:
   HAS_INCREMENTAL = EMAIL_TOOLS.get_inbox_updates is not null
   HAS_STATE = sync_state.inbox.query_state is not null
   IS_RESET = user passed --reset flag
   IS_FULL = user passed --full flag
```

#### Fetching Emails

```
IF IS_RESET:
  # Clear all state, do full fetch
  Clear sync_state.inbox (set query_state, last_sync, mailbox_id to null, seen_email_ids to [])

IF HAS_INCREMENTAL AND HAS_STATE AND NOT IS_RESET AND NOT IS_FULL:
  # Incremental path
  result = call EMAIL_TOOLS.get_inbox_updates({
    sinceQueryState: sync_state.inbox.query_state,
    mailboxId: sync_state.inbox.mailbox_id,
    limit: 100
  })

  IF result.isFullQuery:
    # Server couldn't calculate changes, fell back to full
    emails = result.added
    sync_mode = "full (server fallback)"
  ELSE:
    emails = result.added
    # Remove any seen_email_ids that are in result.removed (they left the inbox)
    Remove result.removed from sync_state.inbox.seen_email_ids
    sync_mode = "incremental"

ELIF HAS_INCREMENTAL:
  # Full query via get_inbox_updates (captures queryState for next time)
  result = call EMAIL_TOOLS.get_inbox_updates({
    mailboxId: sync_state.inbox.mailbox_id,  # null is OK, tool auto-discovers
    limit: 100
  })
  emails = result.added
  sync_mode = "full"

ELSE:
  # Fallback for non-JMAP providers
  emails = call EMAIL_TOOLS.list_emails({ mailboxId: inbox_id, limit: 100 })
  result = { queryState: null }
  sync_mode = "legacy (no incremental sync)"
```

#### Filtering Already-Seen Emails

```
# Remove emails the user already triaged but chose to leave in inbox
IF sync_state.inbox.seen_email_ids is not empty:
  emails = emails.filter(e => e.id NOT IN sync_state.inbox.seen_email_ids)
```

#### Reconciliation (Incremental Mode Only)

**Why:** JMAP incremental sync only returns emails that were added or modified since the
last `queryState`. Emails sitting unchanged in inbox (e.g., flagged in a previous session
but not added to `seen_email_ids`) won't appear in the diff. This step catches them.

```
IF sync_mode == "incremental":
  # Fetch current inbox listing
  inbox_listing = call EMAIL_TOOLS.list_emails({ mailboxId: inbox_id, limit: 50 })
  inbox_ids = inbox_listing.map(e => e.id)

  # Find orphans: in inbox but NOT in incremental results AND NOT in seen_email_ids
  incremental_ids = emails.map(e => e.id)
  orphan_ids = inbox_ids.filter(id =>
    id NOT IN incremental_ids AND
    id NOT IN sync_state.inbox.seen_email_ids
  )

  IF orphan_ids.length > 0:
    # Add orphaned emails to the triage list
    orphan_emails = inbox_listing.filter(e => e.id IN orphan_ids)
    emails = emails.concat(orphan_emails)
    Report: "Found {orphan_ids.length} orphaned email(s) from previous sessions"
```

```
# Report what happened
IF sync_mode == "incremental" AND emails.length == 0:
  Report: "No new emails since {sync_state.inbox.last_sync}"
  STOP (nothing to triage)
```

#### After Triage (Saving State)

```
1. Save new query_state:
   sync_state.inbox.query_state = result.queryState  # (if available)
   sync_state.inbox.last_sync = current ISO timestamp
   sync_state.inbox.mailbox_id = result mailbox ID (or discovered inbox ID)

2. Update seen_email_ids for ALL inbox-staying decisions:
   For each email where user chose "keep", "flag", or "custom" (email stays in inbox):
     Add email.id to sync_state.inbox.seen_email_ids
   NOTE: Any action that does NOT move or delete the email means it stays in inbox.

3. Prune seen_email_ids if > 500 entries:
   Remove oldest entries (beginning of array) to stay at 500

4. Write updated sync-state.yaml
```

### Flags

| Flag | Behavior |
|------|----------|
| (none) | Incremental if state exists, full otherwise |
| `--reset` | Clear ALL sync state, then full fetch |
| `--full` | Full fetch this time, but save new state for next time |

### Reporting

Always report the sync mode in the output:

```
Sync: incremental — 8 new emails (42 total in inbox)
Sync: full — 45 emails
Sync: full (server fallback) — 45 emails (stale state cleared)
Sync: legacy — 45 emails (incremental sync not available)
```
