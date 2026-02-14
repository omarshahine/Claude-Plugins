---
description: View and manage email action routes
argument-hint: "[--add | --disable ID | --enable ID | --remove ID]"
---

# /chief-of-staff:routes

View, add, remove, and toggle email action routes. Action routes map specific emails to specialized agents for active processing during triage.

## Usage

```
/chief-of-staff:routes              # Show all routes with match stats
/chief-of-staff:routes --add        # Interactive route creation
/chief-of-staff:routes --disable N  # Disable route by index
/chief-of-staff:routes --enable N   # Re-enable a disabled route
/chief-of-staff:routes --remove N   # Remove route permanently
```

## What It Shows

1. **Active Routes** by type (sender_email, sender_domain, subject_pattern, combined)
2. **Route targets** — which plugin:agent handles the email
3. **Confidence scores** and match counts
4. **Post-action** — what happens to the email after processing
5. **Disabled Routes** — routes that are toggled off

## Example Output

```
Email Action Routes
===================

## Sender Email Routes (2 routes)
| # | Email | Route Label | Target | Post-Action | Confidence | Matches | Enabled |
|---|-------|-------------|--------|-------------|------------|---------|---------|
| 1 | accounting@vendor.example.com | Process Vendor Invoice | my-plugin:invoice-processor | archive → Invoices | 95% | 12 | Yes |
| 2 | billing@service.example.com | Download Service Invoices | my-plugin:invoice-downloader | none | 95% | 8 | Yes |

## Sender Domain Routes (1 route)
| # | Domain | Subject Filter | Route Label | Target | Post-Action | Confidence | Matches | Enabled |
|---|--------|---------------|-------------|--------|-------------|------------|---------|---------|
| 3 | reports.example.com | Result Available | Download Reports | my-plugin:report-downloader | archive | 95% | 3 | Yes |

## Subject Pattern Routes (0 routes)
(none)

## Combined Routes (0 routes)
(none)

Thresholds:
- Suggest minimum: 80% confidence
- Auto-route minimum: 95% confidence

Actions:
1. Add new route
2. Disable/enable a route
3. Remove a route
```

## Implementation

This command reads and displays data files directly:

1. Read `~/.claude/data/chief-of-staff/email-action-routes.yaml`
   - If file doesn't exist, copy from the example template:
     1. `Glob: ~/.claude/plugins/cache/**/chief-of-staff/**/data/email-action-routes.example.yaml`
     2. Read the example file and Write it to `~/.claude/data/chief-of-staff/email-action-routes.yaml`
     3. Report: "Initialized routes file from template. Use `--add` to create your first route."
2. Format and display tables (grouped by route type)
3. For `--add`: Use AskUserQuestion for interactive creation:
   - Match type (sender_email, sender_domain, subject_pattern, combined)
   - Match value (email address, domain, regex pattern)
   - Optional refinements (subject_pattern, attachment_required)
   - Target plugin and agent name
   - Route label and description
   - Whether to pass attachments
   - Post-action (archive/delete/keep/none)
   - Post-action folder (if archive)
   - Initial confidence (default 0.90 for manual routes)
4. For `--disable N` / `--enable N`: Toggle the `enabled` field on route at index N
5. For `--remove N`: Remove the route at index N entirely (with confirmation)
6. Write updated file back after changes
