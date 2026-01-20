# Rename Agent Plugin

AI-powered file renaming for Claude Code. Analyzes documents (PDFs, images, text files), classifies them, and applies consistent naming patterns.

## Features

- **Document Analysis**: Reads PDFs, images, and text files to understand content
- **Smart Classification**: Identifies document types (receipts, bills, tax documents, bank statements, etc.)
- **Pattern-Based Naming**: Uses customizable templates with tokens like `{Date}`, `{Merchant}`, `{Amount}`
- **Pattern Learning**: Saves patterns for future use when processing similar documents
- **Batch Processing**: Process multiple files at once with consistent naming

## Installation

### 1. Install the Plugin

```bash
/plugin install rename-agent@agent-plugins
```

### 2. Install the CLI Tool

The plugin requires the `rename-agent` CLI to be installed:

**Quick Install:**
```bash
curl -fsSL https://raw.githubusercontent.com/omarshahine/claude-rename-agent/main/install.sh | bash
```

**Or via pip:**
```bash
pip install claude-rename-agent
```

### Prerequisites

- Python 3.10+
- `ANTHROPIC_API_KEY` environment variable set

## Usage

### Via Command

```bash
/rename-agent:rename ~/Downloads/tax-docs
/rename-agent:rename ~/Documents/receipts --pattern "{Date:YYYY-MM-DD} - {Merchant}"
/rename-agent:rename ~/Desktop/statements --dry-run
```

### Via Natural Language

Just ask Claude to rename files:

- "Rename the tax documents in my Downloads folder"
- "Organize these receipts with dates and merchant names"
- "Help me rename these bank statements"

## Pattern Tokens

| Token | Example |
|-------|---------|
| `{Date:YYYY-MM-DD}` | 2024-03-15 |
| `{Year}` | 2024 |
| `{Merchant}` | Amazon |
| `{Amount}` | 125.99 |
| `{Institution}` | Chase Bank |
| `{Form Type}` | K-1, 1099 |
| `{Last 4 Digits}` | 7890 |
| `{Description}` | Annual Statement |

## Document Types

Receipt, Bill, Tax Document, Bank Statement, Invoice, Contract, Medical, Insurance, Investment, Payslip, Identity, Correspondence, Manual, Photo, General

## Links

- **Source**: https://github.com/omarshahine/claude-rename-agent
- **Issues**: https://github.com/omarshahine/claude-rename-agent/issues
