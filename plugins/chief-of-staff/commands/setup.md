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

4. **Discover existing email MCP tools** using ToolSearch:
   ```
   ToolSearch query: "list_mailboxes email"
   ```

   Check results for known providers: `mcp__fastmail__`, `mcp__gmail__`, `mcp__outlook__`

5. **If email tools found**, auto-detect provider:
   - Extract provider name from tool prefix (e.g., `mcp__fastmail__` → "fastmail")
   - Skip to step 7 (verify connection)
   - Confirm with user: "Found [provider] email tools. Using this provider."

6. **If NO email tools found**, guide user through setup:
   ```
   AskUserQuestion:
     questions:
       - question: "No email MCP server detected. Which email provider do you want to set up?"
         header: "Email Provider"
         options:
           - label: "Fastmail (Recommended)"
             description: "Best MCP support, advanced search, bulk operations"
           - label: "Gmail"
             description: "Requires Gmail MCP server"
           - label: "Outlook"
             description: "Requires Microsoft Graph MCP server"
         multiSelect: false
   ```

   Then display setup instructions based on selection:
   ```
   ## Email MCP Setup Required

   To use Chief-of-Staff, you need to add your [PROVIDER] MCP server:

   **Cowork users:**
   1. Go to Settings → Custom Connectors
   2. Click "Add Connector"
   3. Enter:
      - Name: `[provider]` (exactly as shown - lowercase)
      - URL: Your [PROVIDER] MCP server URL
   4. Click Save
   5. Re-run `/chief-of-staff:setup`

   **CLI users:**
   ```
   claude mcp add --transport http [provider] <your-mcp-url>
   ```

   **Need an MCP server?**
   - Fastmail: https://github.com/nicholasgriffintn/fastmail-mcp
   - Gmail: [community MCP servers]
   - Outlook: [community MCP servers]
   ```

   **STOP here** - user must add the MCP connector first, then re-run setup.

7. **Verify email connection**:
   - Load provider tools: `ToolSearch query: "+[provider]"`
   - Call `list_mailboxes` to verify connection works
   - If connection fails, show troubleshooting steps
   - If success, extract folder list for settings.yaml

### Phase 3: Integration Verification

8. Check optional integrations:
   - Try to load parcel-api tools
   - Try to load apple-pim tools
   - Try to load playwright tools

### Phase 4: Configuration Files

9. **Find plugin templates directory**:
   ```
   Glob: ~/.claude/plugins/cache/*/chief-of-staff/*/data/settings.example.yaml
   ```
   Extract the templates path for reading examples.

10. **Read settings.example.yaml** as the template

11. **Create data directory if needed**:
    ```bash
    mkdir -p ~/.claude/data/chief-of-staff
    ```

12. **Create settings.yaml** in `~/.claude/data/chief-of-staff/settings.yaml` with:

   **Persona section:**
   ```yaml
   persona:
     name: "[selected name]"           # e.g., "Friday"
     user_name: "[user's name or null]"
     greeting_style: "[selected style]" # professional, friendly, casual
   ```

   **Email provider section** (based on detected/selected provider):
   ```yaml
   providers:
     email:
       active: [provider]  # fastmail, gmail, or outlook
       mappings:
         # Copy the mappings for the active provider from settings.example.yaml
         [provider]:
           list_mailboxes: mcp__[provider]__list_mailboxes
           list_emails: mcp__[provider]__list_emails
           # ... all other mappings
   ```

   **Discovered folders:**
   ```yaml
   folders:
     inbox_id: "[discovered inbox ID]"
     archive_id: "[discovered archive ID or null]"
     orders_folder_name: "Orders"
     # ... other folder settings
   ```

   **Integration status:**
   ```yaml
   integrations:
     parcel: [true/false based on discovery]
     reminders: [true/false based on discovery]
     newsletters: [true/false based on discovery]
   ```

13. **Write settings.yaml** to `~/.claude/data/chief-of-staff/settings.yaml`

### Phase 5: Generate Summon Command

10. Read the template from `templates/summon-command.md`
11. Replace placeholders:
    - `{{NAME}}` -> Persona name (e.g., "Friday")
    - `{{NAME_LOWER}}` -> Lowercase persona name (e.g., "friday")
    - `{{USER_NAME}}` -> User's name (e.g., "Jane") if set
    - `{{USER_CLAUSE}}` -> " for [user_name]" if set, empty string if null
    - `{{GREETING_STYLE}}` -> Selected style
    - `{{GREETING_INSTRUCTIONS}}` -> Style-specific instructions

**Special handling for email signature based on user_name:**

If user_name is null:
1. Replace the two signature format lines with a single line:
   - `**Signature format:** \`{{NAME}} (AI assistant)\``
2. Replace the example blocks:
   - Change `Example (with user name configured):` to `Example:`
   - Remove the `Example (without user name configured):` block entirely
   - Update the signature in the example to `{{NAME}} (AI assistant)`

If user_name is configured:
1. Replace the two signature format lines with a single line:
   - `**Signature format:** \`{{NAME}} ({{USER_NAME}}'s AI assistant)\``
2. Replace the example blocks:
   - Change `Example (with user name configured):` to `Example:`
   - Remove the `Example (without user name configured):` block entirely
   - Keep the signature as `{{NAME}} ({{USER_NAME}}'s AI assistant)`

This ensures the generated command only shows the relevant signature format.

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
1. Read existing `~/.claude/data/chief-of-staff/settings.yaml` to get current persona name
2. After new persona is configured, delete old command file if name changed
3. Create new command file with new name

Example:
- Old persona: "friday" -> `~/.claude/commands/friday.md`
- New persona: "max" -> Delete `friday.md`, create `max.md`
