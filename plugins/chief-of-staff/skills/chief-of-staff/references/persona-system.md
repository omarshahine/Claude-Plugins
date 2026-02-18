# Persona System Reference

Chief-of-Staff supports a configurable **persona** that gives the assistant a custom identity and dynamic summon command.

## Configuration

Persona settings are stored in `data/settings.yaml`:

```yaml
persona:
  name: Friday            # Assistant's name
  user_name: Jane         # User's name (optional)
  greeting_style: friendly # professional, friendly, casual
```

## Dynamic Summon Command

When configured, a personalized command is created at `~/.claude/commands/<name>.md`:
- Persona "Friday" -> `/friday`
- Persona "Max" -> `/max`
- Persona "Jarvis" -> `/jarvis`

## Summon Command Features

The summon command (`/friday`, etc.) provides:

1. **Quick Assessment**: Inbox status, active deliveries, due reminders
2. **Contextual Suggestions**: Recommends actions based on current state
3. **Sub-command Routing**: `/friday triage`, `/friday parcel`, etc.

## Greeting Styles

| Style | Example |
|-------|---------|
| professional | "Good morning. Here's your current status." |
| friendly | "Good morning! Let's see what we've got today." |
| casual | "Hey! Here's what's happening." |

## Sub-commands

| Command | Routes To |
|---------|-----------|
| `/friday` | Quick assessment + suggestions |
| `/friday triage` | `/chief-of-staff:triage` |
| `/friday parcel` | `/chief-of-staff:parcel` |
| `/friday status` | `/chief-of-staff:status` |
| `/friday daily` | `/chief-of-staff:daily` |
| `/friday reminders` | `/chief-of-staff:reminders` |
| `/friday imessage` | `/chief-of-staff:imessage` |

## Setup

Run `/chief-of-staff:setup` to configure the persona. The setup command will:
1. Ask for persona name and greeting style
2. Generate the summon command from the `assets/summon-command.md` template
3. Save settings to `data/settings.yaml`
