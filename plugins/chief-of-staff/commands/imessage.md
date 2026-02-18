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
/chief-of-staff:imessage read Alex                 # Read messages with Alex
/chief-of-staff:imessage read Alex --limit 50      # Read last 50 messages
/chief-of-staff:imessage read Alex --since 2025-01-01  # Messages since date
/chief-of-staff:imessage search restaurant          # Search all messages for keyword
/chief-of-staff:imessage search "move out" --limit 10   # Search with limit
/chief-of-staff:imessage send Alex "I'll be 10 minutes late"  # Send with confirmation
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

Parse the arguments from `{{ ARGUMENTS }}` and route to the imessage-assistant agent:

{{ ARGUMENTS }}

Use the Task tool to invoke the imessage-assistant agent with the appropriate prompt:

```
subagent_type: "chief-of-staff:imessage-assistant"
```

**Routing logic:**

- No args or `chats` → prompt: "List recent iMessage conversations with resolved contact names. Show the last 20 chats."
- `read <name> [flags]` → prompt: "Read message history with <name>. [Apply --limit N if specified, default 20] [Apply --since DATE if specified]"
- `search <keyword> [flags]` → prompt: "Search all iMessage conversations for '<keyword>'. [Apply --limit N if specified, default 20]"
- `send <name> <message>` → prompt: "Send an iMessage to <name> with the text: <message>. You MUST confirm with the user before sending."
