---
description: Read and send iMessages with contact name resolution
argument-hint: "[chats] [read <name>] [search <keyword>] [send <name> <message>]"
---

# /chief-of-staff:imessage

Read and send iMessages with automatic contact name resolution.

## Usage

```
/chief-of-staff:imessage                           # List recent conversations
/chief-of-staff:imessage chats                      # List recent conversations
/chief-of-staff:imessage read Sarah                 # Read messages with Sarah
/chief-of-staff:imessage read Sarah --limit 50      # Read last 50 messages
/chief-of-staff:imessage read Sarah --since 2025-01-01  # Messages since date
/chief-of-staff:imessage search restaurant          # Search all messages for keyword
/chief-of-staff:imessage search "move out" --limit 10   # Search with limit
/chief-of-staff:imessage send Lora "I'll be 10 minutes late"  # Send with confirmation
```

## Arguments

- **chats** (or no args): List recent conversations with resolved contact names
- **read \<name\> [--limit N] [--since DATE]**: Read message history with a contact
- **search \<keyword\> [--limit N]**: Search across all conversations for a keyword
- **send \<name\> \<message\>**: Send a message (requires confirmation)

## What It Does

1. **Resolves contact names** via Apple Contacts (PIM)
2. **Reads messages** via the `imsg` CLI tool
3. **Searches messages** via direct SQLite query on `chat.db`
4. **Sends messages** only after explicit user confirmation

## Implementation

**IMPORTANT: Run directly in main agent, NOT as a sub-agent.**

The send operation requires `AskUserQuestion` for user confirmation. Sub-agents spawned via Task tool do NOT have access to `AskUserQuestion`. Therefore, this command MUST run directly in the main agent context.

**Workflow:**

Load the imessage-assistant agent instructions as guidance and execute the logic directly in the main agent.

Parse the arguments from `{{ ARGUMENTS }}`:

{{ ARGUMENTS }}

**Routing logic:**

- No args or `chats` → List recent iMessage conversations with resolved contact names (last 20 chats)
- `read <name> [flags]` → Read message history with the specified contact (apply --limit N if specified, default 20; apply --since DATE if specified)
- `search <keyword> [flags]` → Search all iMessage conversations for the keyword (apply --limit N if specified, default 20)
- `send <name> <message>` → Send an iMessage to the contact with the specified text. You MUST confirm with the user via AskUserQuestion before sending.

**Reference:** See `agents/imessage-assistant.md` for detailed implementation guidance on contact resolution, message formatting, and safety requirements.
