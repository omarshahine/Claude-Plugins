## Inbox Action Pattern Reference

This document describes the canonical structure for inbox action agents — agents triggered by email routes that process specific types of emails (invoices, statements, notifications).

### Architecture Overview

An inbox action consists of up to 7 files:

| File | Location | Always | Purpose |
|------|----------|--------|---------|
| Agent | `chief-of-staff-private/agents/inbox-action-{name}.md` | Yes | The autonomous agent that does the work |
| Command | `chief-of-staff-private/commands/{command-name}.md` | Yes | User-facing slash command that delegates to agent |
| Route | `~/.claude/data/chief-of-staff/email-action-routes.yaml` | Yes | Email matching rule (appended to existing file) |
| SKILL.md | `chief-of-staff-private/skills/private-capabilities/SKILL.md` | Yes | Updated with new agent documentation |
| Extraction script | `chief-of-staff-private/skills/{name}/extract_{name}.py` | If PDF | Python script for PDF data extraction |
| Skill doc | `chief-of-staff-private/skills/{name}/SKILL.md` | If complex | Domain knowledge for the agent |
| Settings | `~/.claude/data/chief-of-staff-private/{name}-settings.yaml` | If YNAB | YNAB budget/category/account IDs |

### Agent Template

```markdown
---
description: |
  {description}

  Use when:
  - Triage routes an email from {sender}
  - User wants to {action_verb}
  - User runs /chief-of-staff-private:{command_name}

  <example>
  user: "{example_user_prompt}"
  assistant: "{example_assistant_response}"
  </example>
model: sonnet
tools: "*"
color: {color}
---

# {display_label}

You {action_description}. Your workflow:

1. **Receive** email ID + attachment info from the route processor (or manual invocation)
2. **{step2}**
3. **{step3}**
...

## Email Provider Initialization

If invoked via email route (emailId provided):
1. Read `~/.claude/data/chief-of-staff/settings.yaml`
2. Extract EMAIL_PROVIDER and EMAIL_TOOLS mappings
3. Load tools via ToolSearch: `+{EMAIL_PROVIDER}`
4. Use `EMAIL_TOOLS.get_email` to fetch the email content
{attachment_tools}

If invoked manually with a file path, skip email steps.

If no input provided, search inbox for recent emails from `{sender_email}`{subject_clause}.
```

### Command Template

```markdown
---
description: {short_description}
argument-hint: "{argument_hint}"
---

# /chief-of-staff-private:{command_name}

{one_line_description}

## Usage

\```
/chief-of-staff-private:{command_name}                    # Search inbox for latest
/chief-of-staff-private:{command_name} /path/to/file.pdf  # Process a specific file
/chief-of-staff-private:{command_name} email-id-xxx        # Process a specific email
\```

## What It Does

1. **{step1_label}** -- {step1_desc}
2. **{step2_label}** -- {step2_desc}
...

## Implementation

Delegate to the inbox action agent:

\```
Task:
  subagent_type: "chief-of-staff-private:inbox-action-{name}"
  prompt: |
    {task_prompt}
    Input: [argument from user - path, email ID, or "search inbox"]
\```

If no argument provided, search inbox for recent emails from `{sender_email}`.
```

### Route Entry Template

Routes are appended to `~/.claude/data/chief-of-staff/email-action-routes.yaml`.

**For sender_email match:**
```yaml
    - email: "{sender_email}"
      subject_pattern: "{subject_pattern}"  # Optional
      attachment_required: {true|false}     # Optional
      route:
        plugin: "chief-of-staff-private"
        agent: "inbox-action-{name}"
        label: "{display_label}"
        description: "{route_description}"
        pass_attachments: {true|false}
        post_action: "{archive|none}"
        post_action_folder: "{folder}"      # Optional, only if post_action is archive
      confidence: 0.95
      match_count: 0
      source: "wizard"
      enabled: true
```

**For domain + subject combined match:**
```yaml
  combined:
    - domain: "{sender_domain}"
      subject_pattern: "{subject_pattern}"
      attachment_required: {true|false}    # Optional, at rule level (not inside route:)
      route:
        plugin: "chief-of-staff-private"
        agent: "inbox-action-{name}"
        label: "{display_label}"
        description: "{route_description}"
        pass_attachments: {true|false}
        post_action: "{archive|none}"
        post_action_folder: "{folder}"
      confidence: 0.95
      match_count: 0
      source: "wizard"
      enabled: true
```

After appending, increment `metadata.total_routes` by 1.

### YNAB Integration Pattern

For agents that create YNAB transactions, include this section in the agent:

```markdown
## YNAB Integration (Direct API)

### Settings

Read settings from `~/.claude/data/chief-of-staff-private/{name}-settings.yaml`:

\```yaml
ynab:
  budget_id: null          # Populated after first run
  category_id: null        # Default category
  account_id: null         # Payment account
  payee_name: "{payee_name}"
\```

### API Flow

1. Get YNAB token (try in order):
   - `YNAB_API_TOKEN` environment variable
   - `YNAB_CLI_ACCESS_TOKEN` environment variable
   - macOS Keychain: `security find-generic-password -s 'env/YNAB_API_TOKEN' -a "$USER" -w 2>/dev/null`
2. If no budget_id in settings: `GET https://api.ynab.com/v1/budgets` -> let user pick
3. Show proposed transaction to user for confirmation
4. On confirmation: `POST https://api.ynab.com/v1/budgets/{budget_id}/transactions`

### Transaction Format

\```json
{
  "transaction": {
    "account_id": "{account_id}",
    "date": "YYYY-MM-DD",
    "amount": -AMOUNT_IN_MILLIUNITS,
    "payee_name": "{payee_name}",
    "memo": "{memo}",
    "cleared": "uncleared",
    "subtransactions": []
  }
}
\```

**Note**: YNAB amounts are in milliunits (dollars x 1000). Expenses are negative.

### First-Run Setup

If settings file doesn't exist or budget_id is null:
1. Fetch budgets from YNAB API
2. Ask user to select budget
3. Fetch categories from selected budget
4. Ask user to select default category
5. Fetch accounts and ask user to select payment account
6. Save all IDs to settings file
```

### Filing Cabinet Pattern

For agents that file documents:

```markdown
## PDF Filing

After processing, save the file to the Filing Cabinet:

**Destination**: `~/Library/CloudStorage/OneDrive-Personal/🗄️ Filing Cabinet/{folder_name}/`

**Naming**: `{naming_pattern}`

If the folder doesn't exist, create it.
```

### PDF Extraction Script Skeleton

For agents that extract data from PDFs using pdfplumber:

```python
#!/usr/bin/env python3
"""Extract data from {document_type} PDFs.

Usage: python3 extract_{name}.py <pdf_path>
Output: JSON to stdout
"""

import json
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber not installed. Run: pip3 install pdfplumber", file=sys.stderr)
    sys.exit(1)


def extract(pdf_path: str) -> dict:
    """Extract structured data from the PDF."""
    result = {
        "source_file": pdf_path,
        "line_items": [],
        "total_amount": 0.0,
    }

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            # TODO: Parse page text and populate result
            # Use page.extract_tables() for tabular data

    return result


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <pdf_path>", file=sys.stderr)
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not Path(pdf_path).exists():
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    result = extract(pdf_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```

### SKILL.md Section Template

When adding to `skills/private-capabilities/SKILL.md`, add a section following this pattern:

```markdown
## {Display Name}

**Agent**: `chief-of-staff-private:inbox-action-{name}`

{One paragraph describing what the agent does.}

**Use for:**
- {Use case 1}
- {Use case 2}
- {Use case 3}

**Commands:**
- `/chief-of-staff-private:{command_name}` - {short description}

**{Document} Location:** Filing Cabinet -> {folder}/

**Workflow:**
1. {Step 1}
2. {Step 2}
3. {Step 3}
```

And add any new data files to the Data Files table:

```markdown
| `{name}-settings.yaml` | {Purpose} |
```

### Updating plugin.json Version

After creating all files, bump the patch or minor version in:
`chief-of-staff-private/.claude-plugin/plugin.json`

Use minor bump (1.X.0) for new agents, patch bump (1.0.X) for fixes.

### Existing Inbox Actions (for reference)

| Name | Sender | Action | YNAB | Filing |
|------|--------|--------|------|--------|
| `inbox-action-stc` | accounting@seattletennisclub.org | PDF extraction → YNAB split | 3-way split (Club/Activities/Dining) | Seattle Tennis Club/ |
| `inbox-action-phamatech` | uverify@phamatech.com | URL extraction → form fill → PDF | No | Miles/Phamatech/ |
| `inbox-action-lf-invoice` | notification.intuit.com (+ subject) | PDF extraction → YNAB split | Per-trip split | Local Foreigner/ |
| `inbox-action-netjets` | billing@netjets.com | Attachment download → rename | No | NetJets/Invoices/ |
