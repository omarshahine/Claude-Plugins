---
description: Configure Chief-of-Staff email provider and integrations
---

# /chief-of-staff:setup

Configure your email provider, persona, and verify all integrations are working.

## What This Command Does

1. Configure persona (name, greeting style)
2. Verify email provider connectivity (Fastmail, Gmail, or Outlook)
3. Discover folder structure
4. Verify optional integrations:
   - Parcel API (for package tracking)
   - Apple PIM (for reminders)
   - Playwright (for newsletter unsubscribe)
5. Create initial settings files
6. Generate personalized summon command (e.g., `/friday`)

## Implementation

### Phase 1: Persona Configuration

1. Ask user for persona name via AskUserQuestion:
```
AskUserQuestion:
  questions:
    - question: "What would you like to name your Chief-of-Staff? (e.g., Friday, Max, Jarvis)"
      header: "Persona"
      options:
        - label: "Friday"
          description: "Inspired by Tony Stark's AI assistant"
        - label: "Max"
          description: "A friendly, efficient assistant"
        - label: "Jarvis"
          description: "Classic AI butler persona"
      multiSelect: false
```

2. Ask for user's name (optional):
```
AskUserQuestion:
  questions:
    - question: "What's your name? (for personalized greetings, or skip for generic greetings)"
      header: "Your Name"
      options:
        - label: "Skip"
          description: "Use generic greetings without my name"
      multiSelect: false
```

3. Ask for greeting style:
```
AskUserQuestion:
  questions:
    - question: "What greeting style do you prefer?"
      header: "Style"
      options:
        - label: "Friendly (Recommended)"
          description: "Warm and conversational: 'Good morning! Let's see what we've got today.'"
        - label: "Professional"
          description: "Formal and efficient: 'Good morning. Here's your inbox status.'"
        - label: "Casual"
          description: "Relaxed and informal: 'Hey! Here's what's happening.'"
      multiSelect: false
```

### Phase 2: Email Provider Setup

4. Read `data/settings.example.yaml` to get the template
5. Ask user which email provider they're using via AskUserQuestion:
```
AskUserQuestion:
  questions:
    - question: "Which email provider are you using?"
      header: "Email"
      options:
        - label: "Fastmail (Recommended)"
          description: "Full MCP integration with advanced search"
        - label: "Gmail"
          description: "Gmail MCP server required"
        - label: "Outlook"
          description: "Microsoft Graph MCP required"
```

6. Use ToolSearch to load email MCP tools (e.g., `+fastmail list mailboxes`)
7. Call list_mailboxes to verify connection

### Phase 3: Integration Verification

8. Check optional integrations:
   - Try to load parcel-api tools
   - Try to load apple-pim tools
   - Try to load playwright tools

### Phase 4: Configuration Files

9. Create `data/settings.yaml` with:
   - Persona configuration (name, user_name, greeting_style)
   - Provider configuration
   - Discovered folder IDs
   - Integration status

### Phase 5: Generate Summon Command

10. Read the template from `templates/summon-command.md`
11. Replace placeholders:
    - `{{NAME}}` -> Persona name (e.g., "Friday")
    - `{{NAME_LOWER}}` -> Lowercase persona name (e.g., "friday")
    - `{{USER_NAME}}` -> User's name (e.g., "Jane") if set
    - `{{USER_CLAUSE}}` -> " for [user_name]" if set, empty string if null
    - `{{GREETING_STYLE}}` -> Selected style
    - `{{GREETING_INSTRUCTIONS}}` -> Style-specific instructions

**Special handling for email signature when user_name is null:**
If user_name is null, replace the signature format line with:
- `**Signature format:** \`{{NAME}} (AI assistant)\``

This ensures consistency with batch-processor and inbox-interviewer agents.

12. Greeting instructions by style:
    - **professional**: "Be formal and efficient. Use complete sentences. Avoid exclamation marks. Example: 'Good morning. Here's your current status.'"
    - **friendly**: "Be warm and conversational. Use occasional exclamation marks. Example: 'Good morning! Let's see what we've got today.'"
    - **casual**: "Be relaxed and informal. Use contractions freely. Example: 'Hey! Here's what's happening.'"

13. Write the generated command to `~/.claude/commands/<name>.md` (lowercase)

14. If a previous persona command exists with a different name, remove it

## Output

```
# Chief-of-Staff Setup Complete

## Persona
- Name: Friday
- Your Name: Jane
- Style: Friendly
- Summon Command: /friday

## Email Provider
- Provider: Fastmail
- Connection: ✓ Success
- Folders: 42 discovered

## Integrations
- Parcel API: ✓ Connected (package tracking enabled)
- Apple PIM: ✓ Connected (reminders enabled)
- Playwright: ✓ Available (newsletter unsubscribe enabled)

## Folder Structure
Key folders discovered:
- Inbox
- Archive
- Orders
- Financial
- Travel
...

## Next Steps
1. Summon your assistant with `/friday`
2. Or try specific commands:
   - `/friday triage` - Process your inbox
   - `/friday parcel` - Track packages
   - `/friday status` - Full dashboard
```

## Handling Persona Changes

If the user re-runs setup:
1. Read existing `data/settings.yaml` to get current persona name
2. After new persona is configured, delete old command file if name changed
3. Create new command file with new name

Example:
- Old persona: "friday" -> `~/.claude/commands/friday.md`
- New persona: "max" -> Delete `friday.md`, create `max.md`
