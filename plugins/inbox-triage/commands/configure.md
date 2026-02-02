---
description: Configure inbox-triage integration settings
argument-hint: "[--parcel on|off] [--reminders on|off] [--newsletter on|off] [--show]"
---

# /inbox-triage:configure

View and modify integration settings for inbox-interviewer. These settings control which specialized features are available during interview mode.

## Usage

```
/inbox-triage:configure              # Show current settings
/inbox-triage:configure --show       # Show current settings (explicit)
/inbox-triage:configure --parcel on  # Enable Parcel integration
/inbox-triage:configure --parcel off # Disable Parcel integration
/inbox-triage:configure --reminders on|off
/inbox-triage:configure --newsletter on|off
```

## Available Integrations

| Integration | Description | When Enabled |
|-------------|-------------|--------------|
| **Parcel** | Package tracking via inbox-to-parcel | "Add to Parcel" option for shipping emails |
| **Reminders** | Reminder creation via Apple PIM | Auto-suggest reminder for action items |
| **Newsletter** | Newsletter management via newsletter-unsubscriber | "Delete + Unsubscribe" option |
| **Filing** | Core filing feature (always enabled) | Folder suggestions based on rules |

## Implementation

1. **Find data directory**: Use Glob to find `~/.claude/plugins/cache/*/inbox-triage/*/data/settings.yaml`

2. **Read current settings**: Load the `integrations` section from settings.yaml

3. **If no arguments or --show**: Display current settings:
```
Inbox Triage Integration Settings
================================

Parcel (inbox-to-parcel):     ENABLED
  - Auto-archive to: Orders

Reminders (Apple PIM):        ENABLED
  - Default list: Reminders
  - Auto-detect action items: Yes

Newsletter (newsletter-unsubscriber): ENABLED
  - Offer unsubscribe: Yes

Filing (core):                ENABLED (always on)
  - Min confidence: 70%
```

4. **If arguments provided**: Update the settings.yaml file:
   - Parse arguments: `--parcel`, `--reminders`, `--newsletter` with `on` or `off`
   - Update the corresponding `integrations.[name].enabled` value
   - Write back to settings.yaml
   - Confirm the change

## Examples

**Show settings:**
```
> /inbox-triage:configure

Inbox Triage Integration Settings
================================
Parcel:      ENABLED
Reminders:   ENABLED
Newsletter:  ENABLED
Filing:      ENABLED (always on)
```

**Disable Parcel:**
```
> /inbox-triage:configure --parcel off

Updated: Parcel integration DISABLED
Interview mode will no longer offer "Add to Parcel" for shipping emails.
```

**Enable Newsletter:**
```
> /inbox-triage:configure --newsletter on

Updated: Newsletter integration ENABLED
Interview mode will offer "Delete + Unsubscribe" for detected newsletters.
```

## Notes

- Changes take effect immediately for new interview sessions
- Filing cannot be disabled (it's the core feature)
- Settings are stored in the plugin's data directory
