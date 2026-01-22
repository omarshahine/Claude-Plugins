# Agent-Plugins Development Guide

This repository is a Claude Code plugin marketplace (`omarshahine-agent-plugins`) containing reusable plugins for travel, file organization, and personal information management.

## Repository Structure

```
Agent-Plugins/
├── .claude-plugin/
│   └── marketplace.json       # Marketplace definition (plugins registry)
├── plugins/
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
│   └── apple-pim/             # macOS Calendar, Reminders, Contacts
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── .mcp.json          # MCP server configuration
│       ├── agents/            # pim-assistant
│       ├── commands/          # calendars, reminders, contacts slash commands
│       ├── skills/
│       ├── swift/             # Native Swift CLIs (calendar-cli, reminder-cli, contacts-cli)
│       ├── mcp-server/        # Node.js MCP server wrapping Swift CLIs
│       └── setup.sh           # Build script for Swift + Node deps
├── README.md                  # User-facing documentation
└── CLAUDE.md                  # This file (development instructions)
```

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

# Reinstall plugin after changes
/plugin install travel-agent@omarshahine-agent-plugins
```

### Testing Agents

Use the Task tool to test agents:
```
Task(subagent_type="travel-agent:flighty", prompt="List upcoming flights")
```

### Testing MCP Servers

Check MCP status:
```
/mcp
```

For apple-pim, ensure setup script has been run:
```bash
./plugins/apple-pim/setup.sh
```

## Plugin-Specific Notes

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

### apple-pim

**Architecture:**
1. Swift CLIs (`calendar-cli`, `reminder-cli`, `contacts-cli`) use EventKit/Contacts frameworks
2. Node.js MCP server (`mcp-server/server.js`) wraps CLIs and exposes tools
3. Slash commands (`/apple-pim:calendars`, `/apple-pim:reminders`, `/apple-pim:contacts`) provide structured access
4. Agent (`pim-assistant`) and skill provide natural language interface

**Components:**
```
plugins/apple-pim/
├── .claude-plugin/plugin.json    # Plugin manifest with mcpServers reference
├── .mcp.json                     # MCP server config (uses ${CLAUDE_PLUGIN_ROOT})
├── agents/pim-assistant.md       # Natural language PIM assistant
├── commands/
│   ├── calendars.md              # /apple-pim:calendars command
│   ├── reminders.md              # /apple-pim:reminders command
│   └── contacts.md               # /apple-pim:contacts command
├── skills/apple-pim/SKILL.md     # EventKit/Contacts framework knowledge
├── swift/                        # Native Swift CLI tools
│   ├── Package.swift
│   └── Sources/
│       ├── CalendarCLI/          # Calendar operations
│       ├── ReminderCLI/          # Reminder operations
│       └── ContactsCLI/          # Contact operations
├── mcp-server/
│   ├── package.json
│   └── server.js                 # MCP server wrapping Swift CLIs
└── setup.sh                      # Build script
```

**MCP Tools (21 total):**

Calendar (7):
- `calendar_list` - List all calendars
- `calendar_events` - List events (supports `lastDays`/`nextDays` OR `from`/`to`)
- `calendar_get` - Get single event by ID
- `calendar_search` - Search by title/notes/location
- `calendar_create` - Create event with title, start, end/duration, location, notes, alarms
- `calendar_update` - Update event fields
- `calendar_delete` - Delete event

Reminders (8):
- `reminder_lists` - List all reminder lists
- `reminder_items` - List reminders (filterable by list, completion status)
- `reminder_get` - Get single reminder by ID
- `reminder_search` - Search by title/notes
- `reminder_create` - Create with title, list, due date, priority (0/1/5/9), notes
- `reminder_complete` - Mark complete (or undo)
- `reminder_update` - Update fields
- `reminder_delete` - Delete reminder

Contacts (7):
- `contact_groups` - List contact groups
- `contact_list` - List contacts (filterable by group)
- `contact_search` - Search by name/email/phone
- `contact_get` - Get full details including photo
- `contact_create` - Create with name, email, phone, org, etc.
- `contact_update` - Update fields
- `contact_delete` - Delete contact

**Building:**
```bash
cd plugins/apple-pim
./setup.sh  # Builds Swift CLIs and installs npm deps
```

**Testing:**
```bash
# Test Swift CLIs directly
./swift/.build/release/calendar-cli list
./swift/.build/release/reminder-cli lists
./swift/.build/release/contacts-cli search "John"

# Test via Claude Code
/apple-pim:calendars events
/apple-pim:reminders items
/apple-pim:contacts search "John"
```

**Permissions:**
Users must grant Calendar, Reminders, and Contacts access in System Settings > Privacy & Security.

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
1. Run setup script (for apple-pim)
2. Check `/mcp` for server status
3. Restart Claude Code after MCP changes

### Agent not being invoked
- Check description has clear trigger examples
- Verify tools list includes required tools
- Test manually via Task tool

## Versioning

Bump version in:
1. `plugins/<plugin>/.claude-plugin/plugin.json`
2. `.claude-plugin/marketplace.json`

After version bump, users should reinstall:
```bash
/plugin install <plugin>@omarshahine-agent-plugins
```
