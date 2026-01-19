# Claude-Plugins

A personal plugin marketplace for Claude Code. Contains reusable plugins that can be shared across projects and machines.

## Installation

Add this marketplace to Claude Code:

```bash
# Add to known_marketplaces.json or use CLI if available
claude plugin marketplace add omarshahine/Claude-Plugins
```

Then install plugins:

```bash
claude plugin install travel-agent@claude-plugins
```

## Available Plugins

### travel-agent

Reusable travel-related agents for flight research and tracking:

| Agent | Description |
|-------|-------------|
| `google-flights` | Search Google Flights for airfare pricing estimates |
| `ita-matrix` | Search ITA Matrix for detailed fare codes and rules |
| `flighty` | Query Flighty app for flight tracking data |
| `tripsy` | Query Tripsy app for trip/hotel information |

**Install:**
```bash
claude plugin install travel-agent@claude-plugins
```

**Use agents via Task tool:**
```
Task(subagent_type="travel-agent:google-flights", prompt="Search business class SEA to HKG Dec 2026")
Task(subagent_type="travel-agent:flighty", prompt="List upcoming flights")
```

## Creating New Plugins

1. Create a new directory under `plugins/`
2. Add `.claude-plugin/plugin.json` with metadata
3. Add agents, skills, or commands as needed
4. Update this README

### Plugin Structure

```
plugins/
└── my-plugin/
    ├── .claude-plugin/
    │   └── plugin.json
    ├── agents/
    │   └── my-agent.md
    ├── skills/
    │   └── my-skill/
    │       └── SKILL.md
    ├── commands/
    │   └── my-command.md
    └── README.md
```

## License

MIT
