---
description: Rename files intelligently using AI-powered content analysis
argument-hint: "[path] [--pattern pattern] [--dry-run]"
---

# Rename Command

Rename files based on their content using the `rename-agent` CLI.

## Usage

```
/rename-agent:rename [path] [options]
```

## Examples

```
/rename-agent:rename ~/Downloads/tax-docs
/rename-agent:rename ~/Documents/receipts --pattern "{Date:YYYY-MM-DD} - {Merchant}"
/rename-agent:rename ~/Desktop/statements --dry-run
```

## Instructions

When this command is invoked:

1. **Check installation**: First verify `rename-agent` is installed by running `rename-agent --help`. If not installed, show the user the installation instructions.

2. **Preview files**: If a path is provided, run `rename-agent preview <path>` to show the user what files are available.

3. **Determine pattern**: Based on the document types found, suggest an appropriate naming pattern or use the pattern provided by the user.

4. **Dry run first**: Always run with `--dry-run` first to show the user what renames will happen:
   ```bash
   rename-agent --files <path> --pattern "<pattern>" --dry-run
   ```

5. **Execute**: If the user approves, execute the rename:
   ```bash
   rename-agent --files <path> --pattern "<pattern>"
   ```

## Arguments

Pass arguments directly to the rename-agent CLI:

- `path` - Directory or file to process
- `--pattern` - Custom naming pattern with tokens like `{Date:YYYY-MM-DD}`, `{Merchant}`, etc.
- `--dry-run` - Preview changes without executing
- `--type` - Filter by document type (receipt, tax_document, bank_statement, etc.)

If no arguments provided, start interactive mode with `rename-agent`.
