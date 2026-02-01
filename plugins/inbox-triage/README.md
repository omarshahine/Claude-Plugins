# inbox-triage

Self-learning email triage with pattern recognition and automated email digests.

## Features

- **Pattern Learning**: Discovers filing patterns from existing folder organization
- **Smart Triage**: Matches emails against learned rules with confidence scoring
- **Always Confirm**: Never auto-files - all moves require user confirmation
- **Active Learning**: Improves based on your decisions
- **Automated Digest**: Summarizes automated emails with priority categorization
- **Organization Analysis**: Analyzes Trash/Archive for optimization opportunities

## Commands

| Command | Description |
|---------|-------------|
| `/inbox-triage:setup` | Configure email provider |
| `/inbox-triage:learn` | Bootstrap rules from existing folders |
| `/inbox-triage:triage` | Process inbox with confirmation |
| `/inbox-triage:digest` | Summarize automated emails |
| `/inbox-triage:analyze` | Find Trash/Archive patterns |
| `/inbox-triage:suggest` | Recommend folder improvements |
| `/inbox-triage:rules` | View/manage filing rules |

## Quick Start

```bash
# 1. Configure email provider
/inbox-triage:setup

# 2. Learn patterns from existing folders
/inbox-triage:learn

# 3. Process your inbox
/inbox-triage:triage
```

## How It Works

### Bootstrap Learning

1. Analyzes your existing folder organization
2. Samples emails from each folder
3. Extracts sender domain patterns
4. Calculates confidence based on exclusivity
5. Presents rules for your confirmation

### Confidence Scoring

| Confidence | Meaning |
|------------|---------|
| 90%+ | High reliability - consistent folder match |
| 70-89% | Good match - some variation |
| <70% | Not suggested - unreliable |

### Active Learning

| Action | Effect |
|--------|--------|
| Confirm | +5% confidence |
| Reject | -15% confidence |
| Correct | New rule created |

## Provider Support

- **Fastmail** (active)
- Gmail (future)
- Outlook (future)

## Requirements

- Email MCP server configured
- Existing folder structure to learn from

## License

MIT
