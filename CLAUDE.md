# Agent-Plugins Development Guide

This repository is a Claude Code plugin marketplace (`omarshahine-agent-plugins`) containing reusable plugins for email management, travel, file organization, and personal information management.

## Repository Structure

```
Agent-Plugins/
├── .claude-plugin/
│   └── marketplace.json       # Marketplace definition (plugins registry)
├── plugins/
│   ├── chief-of-staff/        # THE MAIN ORCHESTRATOR PLUGIN
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── agents/            # 13 sub-agents (inbox-interviewer, inbox-to-parcel, etc.)
│   │   ├── commands/          # 14 slash commands (triage, parcel, reminders, etc.)
│   │   ├── skills/
│   │   │   └── chief-of-staff/
│   │   │       └── SKILL.md   # Core orchestrator knowledge
│   │   ├── data/              # User data (gitignored) with .example templates
│   │   ├── assets/            # Templates, patterns, icons used in output
│   │   └── references/        # Documentation loaded as needed by agents
│   ├── travel-agent/          # Flight research and trip tracking
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── agents/            # google-flights, ita-matrix, flighty, tripsy
│   │   └── commands/          # Slash commands for each agent
│   ├── rename-agent/          # AI-powered file renaming
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── skills/
│   │   └── commands/
│   └── credit-card-benefits/  # Credit card benefit tracking
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── agents/
│       ├── commands/
│       └── data/
├── README.md                  # User-facing documentation
└── CLAUDE.md                  # This file (development instructions)
```

**External plugins** (sourced from separate GitHub repos):
- **apple-pim** - macOS Calendar, Reminders, Contacts (sourced from `omarshahine/Apple-PIM-Agent-Plugin`)

## Plugin Development

### Adding a New Plugin

1. Create directory: `plugins/my-plugin/`
2. Add plugin manifest: `plugins/my-plugin/.claude-plugin/plugin.json`
3. Add to marketplace: Update `.claude-plugin/marketplace.json`
4. Document in README.md

### Plugin Manifest (plugin.json)

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Short description",
  "author": { "name": "Your Name" },
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"]
}
```

For plugins with MCP servers, add:
```json
{
  "mcpServers": "./.mcp.json"
}
```

### MCP Environment Variables

**IMPORTANT**: This repo is PUBLIC. Never hardcode URLs or secrets in plugin configs.

MCP servers use `${VAR}` syntax for environment variables (e.g., `${FASTMAIL_MCP_URL}`). These variables must be set in `.claude/settings.local.json` (which is globally gitignored):

```json
{
  "env": {
    "FASTMAIL_MCP_URL": "https://your-fastmail-mcp.workers.dev/mcp"
  },
  "permissions": { ... }
}
```

**Why `.claude/settings.local.json`?**
- Globally gitignored via `~/.config/git/ignore`
- Per-project, so different projects can have different values
- Loaded automatically by Claude Code
- Variables are expanded in MCP configs

**Pattern for plugin MCP configs**:
```json
// In plugin.json - uses env var (safe to commit)
{
  "mcpServers": {
    "fastmail": {
      "type": "http",
      "url": "${FASTMAIL_MCP_URL}"
    }
  }
}
```

```json
// In .claude/settings.local.json - actual URL (never committed)
{
  "env": {
    "FASTMAIL_MCP_URL": "https://fastmail-mcp-remote.your-subdomain.workers.dev/mcp"
  }
}
```

### Agent Definition

Agents go in `plugins/<plugin>/agents/<agent-name>.md`:

```yaml
---
description: |
  When to use this agent...

  <example>
  user: "Example prompt"
  assistant: "How Claude should respond"
  </example>
model: haiku  # or sonnet, opus
tools:
  - mcp__server__tool_name
  - Bash
color: blue  # Optional: blue, green, yellow, red, purple
---

# Agent Name

System prompt instructions for the agent...
```

### Skill Definition

Skills go in `plugins/<plugin>/skills/<skill-name>/SKILL.md`:

```yaml
---
description: |
  Knowledge about topic X. Use when discussing...
---

# Skill Content

Reference documentation, APIs, patterns, etc.
```

### Skill Development Best Practices

Follow these conventions when creating or modifying skills:

**Folder structure:**
```
skills/<skill-name>/
├── SKILL.md              # Main skill file (under 5,000 words)
├── scripts/              # Executable scripts the skill uses
├── references/           # Verbose docs loaded on demand via Read tool
└── assets/               # Static files referenced by path only
```

**SKILL.md frontmatter:**
```yaml
---
name: my-skill            # kebab-case, max 64 chars (recommended)
description: |
  WHAT this skill does.
  Use when:
  - Trigger condition 1
  - Trigger condition 2
  - Explicit phrase: "exact words user might say"
---
```

**Key rules:**
- `name:` — Recommended in skills (unlike commands, where it breaks autocomplete)
- `description:` — Must include WHAT it does + WHEN to trigger with bulleted list of trigger phrases
- **Progressive disclosure** — Keep SKILL.md under 5,000 words. Move verbose reference material to `references/` files and link from SKILL.md
- **References vs assets** — `references/` files are loaded into context via Read tool; `assets/` are referenced by path only (images, templates, JSON patterns)
- **No README.md** inside skill folders — SKILL.md is the single entry point

### Command Definition

Commands go in `plugins/<plugin>/commands/<command-name>.md`:

```yaml
---
description: Short description for autocomplete
argument-hint: "[optional args hint]"
allowed-tools:
  - Bash
  - mcp__server__tool
---

# Command instructions...
```

**Important**: Do NOT include a `name:` field - name comes from filename.

## Testing Plugins

### Local Development

Plugins in this repo are automatically available when the marketplace is added:

```bash
# Add marketplace (one time)
/plugin marketplace add omarshahine/Agent-Plugins

# Install plugin (first time only - plugins auto-update when configured)
/plugin install chief-of-staff@omarshahine-agent-plugins
```

**Note:** Plugins auto-update when `autoUpdates: true` is set in plugin settings. Manual reinstall is only needed if auto-updates are disabled or to force an immediate update.

### Testing Agents

Use the Task tool to test agents:
```
Task(subagent_type="chief-of-staff:inbox-interviewer", prompt="Triage my inbox")
Task(subagent_type="travel-agent:flighty", prompt="List upcoming flights")
```

### Testing MCP Servers

Check MCP status:
```
/mcp
```

For plugins with bundled MCP servers (e.g., apple-pim from external repo), ensure any required setup scripts have been run. See individual plugin documentation.

## Plugin-Specific Notes

### chief-of-staff (Main Orchestrator)

Chief-of-Staff is the "uber orchestrator" - the main plugin that consolidates email management, package tracking, reminder creation, and newsletter management.

**Architecture:**
```
chief-of-staff/
├── agents/
│   ├── inbox-interviewer.md       # Main interactive triage (questions-first)
│   ├── inbox-to-parcel.md         # Package tracking from shipping emails
│   ├── inbox-to-reminder.md       # Create reminders from action items
│   ├── newsletter-unsubscriber.md # Handle newsletter unsubscription
│   ├── digest-generator.md        # Summarize automated emails
│   ├── organization-analyzer.md   # Analyze Trash/Archive patterns
│   ├── pattern-learner.md         # Bootstrap filing rules from folders
│   ├── inbox-triage.md            # Apply learned rules to inbox
│   ├── folder-optimizer.md        # Suggest folder reorganization
│   ├── decision-learner.md        # Learn from triage decisions
│   ├── batch-html-generator.md    # Visual batch triage interface
│   ├── batch-processor.md         # Execute batch triage decisions
│   └── imessage-assistant.md      # Read and send iMessages via CLI
├── commands/
│   ├── setup.md                   # Configure email provider
│   ├── daily.md                   # Full daily orchestration
│   ├── status.md                  # Quick dashboard
│   ├── triage.md                  # Interactive interview mode
│   ├── batch.md                   # Visual HTML batch mode
│   ├── parcel.md                  # Process shipping emails
│   ├── reminders.md               # Create reminders from emails
│   ├── unsubscribe.md             # Unsubscribe from newsletters
│   ├── digest.md                  # Summarize automated emails
│   ├── learn.md                   # Bootstrap filing rules
│   ├── analyze.md                 # Analyze Trash/Archive
│   ├── optimize.md                # Suggest folder improvements
│   ├── rules.md                   # View/manage filing rules
│   └── imessage.md                # Read, search, send iMessages
├── skills/chief-of-staff/SKILL.md # Core knowledge
├── data/                          # User data (gitignored)
│   ├── .gitignore
│   ├── settings.example.yaml
│   ├── user-preferences.example.yaml
│   ├── filing-rules.example.yaml
│   ├── delete-patterns.example.yaml
│   ├── decision-history.example.yaml
│   ├── interview-state.example.yaml
│   ├── batch-state.example.yaml
│   └── newsletter-lists.example.yaml
├── assets/
│   ├── batch-triage.html          # HTML batch interface template
│   ├── shipping-patterns.json     # Carrier detection, tracking regex
│   ├── newsletter-patterns.json   # RFC headers, bulk sender patterns
│   └── summon-command.md          # Dynamic command generation template
└── references/
    ├── email-provider-init.md     # Standard email provider initialization pattern
    └── email-incremental-fetch.md # JMAP incremental sync documentation
```

**Key Concepts:**

1. **Questions-First Workflow**: COLLECT → EXECUTE → LEARN
   - COLLECT: Ask questions for each email (no API calls)
   - EXECUTE: Run all actions in bulk (efficient)
   - LEARN: Record decisions, update confidence

2. **Sub-Agent Delegation**: Commands delegate to agents via Task tool
   ```
   subagent_type: "chief-of-staff:inbox-to-parcel"
   ```

3. **Data Files**: All user data in `data/` folder (gitignored)
   - Copy `.example.yaml` files to create actual configs
   - `settings.yaml` - Email provider, paths
   - `filing-rules.yaml` - Learned patterns with confidence
   - `user-preferences.yaml` - Sender overrides, never-file lists

4. **MCP Dependencies**:
   - Email MCP (required, user-configured) - Fastmail, Gmail, or Outlook
   - Parcel API MCP (optional) - Package tracking
   - Apple PIM MCP (optional) - Reminders, Contacts
   - Playwright plugin (optional) - Newsletter unsubscribe web forms
   - imsg CLI (optional) - iMessage read/send (`brew install steipete/tap/imsg`)

5. **Provider-Agnostic Email Access** (CRITICAL):
   - NEVER hardcode `mcp__fastmail__*` or any provider-specific tool names in agents or commands
   - Always read `settings.yaml` first to get `EMAIL_PROVIDER` and `EMAIL_TOOLS` mappings
   - Load tools dynamically: `ToolSearch("+{EMAIL_PROVIDER}")`
   - Reference tools as `EMAIL_TOOLS.list_emails`, `EMAIL_TOOLS.bulk_move`, etc.
   - See `references/email-provider-init.md` for the standard initialization pattern
   - Exception: agent `allowedTools` frontmatter can't be dynamic — use `tools: "*"` or a broad tool list

**Adding Sub-Agents:**

1. Create agent file in `agents/`
2. Use `chief-of-staff:` prefix in Task tool calls
3. Reference data files with `chief-of-staff/*/data/` paths
4. Follow the provider-agnostic email pattern (see point 5 above)
5. Update SKILL.md with new agent info

**Private Extensions:**

Users can extend COS with private agents by creating a separate plugin (e.g., `chief-of-staff-private`):

```markdown
# skills/private-capabilities/SKILL.md
---
description: |
  Private agents available to Chief-of-Staff:
  - filing-cabinet-organizer: Manage Filing Cabinet documents
  - netjets-invoice-downloader: Download NetJets invoices
---

# Private Chief-of-Staff Capabilities

## Filing Cabinet
Use `chief-of-staff-private:filing-cabinet-organizer` for document organization.

## NetJets
Use `chief-of-staff-private:netjets-invoice-downloader` for invoice management.
```

### travel-agent

**External dependencies:**
- `fast-flights` Python package for google-flights
- `playwright@claude-plugins-official` plugin for ita-matrix
- Flighty and Tripsy apps for local database queries

**Database paths:**
- Flighty: `~/Library/Containers/com.flightyapp.flighty/Data/Documents/MainFlightyDatabase.db`
- Tripsy: `~/Library/Group Containers/group.app.tripsy.ios/Tripsy.sqlite`

### rename-agent

**External dependency:**
- `claude-rename-agent` CLI tool (pip install or curl installer)

**Source repository:** https://github.com/omarshahine/claude-rename-agent

### apple-pim (External Plugin)

**Source:** https://github.com/omarshahine/Apple-PIM-Agent-Plugin

This plugin is sourced from an external GitHub repository rather than being bundled in this marketplace. It provides native macOS integration for Calendar, Reminders, and Contacts.

**Why external?** The plugin has its own build system (Swift CLIs + Node.js MCP server) and benefits from independent versioning.

**Usage:** Install via this marketplace - the plugin is listed here but code lives in the external repo:
```bash
/plugin install apple-pim@omarshahine-agent-plugins
```

See the [Apple-PIM-Agent-Plugin repo](https://github.com/omarshahine/Apple-PIM-Agent-Plugin) for full documentation.

### credit-card-benefits

**Architecture:**
- Tracks benefits across multiple premium credit cards
- Anniversary-aware - resets benefits based on card member anniversary
- Integrates with YNAB for transaction matching

**Data files:**
- `data/checklist.yaml` - Benefit usage tracking
- `data/settings.yaml` - Card configurations, data sources

## Common Issues

### Plugin not loading
1. Check `plugin.json` syntax
2. Verify plugin is in `marketplace.json`
3. Clear cache: `rm -rf ~/.claude/plugins/cache/omarshahine-agent-plugins/<plugin>`
4. Reinstall: `/plugin install <plugin>@omarshahine-agent-plugins`

### Commands not showing in autocomplete
- Remove any `name:` field from command frontmatter
- Command name comes from filename automatically

### MCP server not connecting
1. Run setup script if the plugin has one (check plugin's README)
2. Check `/mcp` for server status
3. Restart Claude Code after MCP changes
4. Verify environment variables are set in `.claude/settings.local.json`

### Agent not being invoked
- Check description has clear trigger examples
- Verify tools list includes required tools
- Test manually via Task tool

### Sub-agent not found
- Verify agent file exists in `agents/` directory
- Check `subagent_type` uses correct prefix (e.g., `chief-of-staff:inbox-to-parcel`)
- Bump plugin version to trigger auto-update

## Versioning

### Version Bump Rules

**ALWAYS bump both versions when making changes:**

1. **Plugin version** in `plugins/<plugin>/.claude-plugin/plugin.json`
2. **Marketplace version** in `.claude-plugin/marketplace.json` (metadata.version)

The marketplace version must be bumped whenever ANY child plugin changes. This ensures users get updates.

### Semantic Versioning

Use **patch version bumps** (1.0.X → 1.0.X+1) for most changes:
- Bug fixes
- Small improvements
- Config changes
- Documentation updates
- Refactoring

Use **minor version bumps** (1.X.0 → 1.X+1.0) for:
- New features, commands, or agents
- Significant new functionality

Use **major version bumps** (X.0.0 → X+1.0.0) only for:
- Breaking changes to command syntax or behavior
- Removing functionality
- Significant architectural changes

**Example workflow:**
```
# Fixing a bug in chief-of-staff (currently 1.0.0, marketplace 1.0.0)
1. Make the fix
2. Bump chief-of-staff: 1.0.0 → 1.0.1
3. Bump marketplace: 1.0.0 → 1.0.1
4. Update plugin entry in marketplace.json to match new version
```

### Where to Update

| Change Type | Update Plugin Version | Update Marketplace Version | Update Plugin Entry in marketplace.json |
|-------------|----------------------|---------------------------|----------------------------------------|
| Plugin change | ✓ | ✓ | ✓ |
| New plugin added | ✓ | ✓ | Add new entry |
| Marketplace-only change | - | ✓ | - |

After version bump, plugins auto-update on next Claude Code session (if auto-updates enabled).
