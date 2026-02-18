#!/bin/bash
# Wrapper script to launch Parcel MCP server with API key
# Priority: 1. .env file (more reliable), 2. macOS Keychain (fallback)

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$SCRIPT_DIR/.."
ENV_FILE="$PLUGIN_ROOT/.env"

# Try .env file first (more reliable for MCP servers)
if [ -f "$ENV_FILE" ]; then
  # Source the .env file, handling quotes properly
  while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
    # Remove surrounding quotes from value
    value="${value%\"}"
    value="${value#\"}"
    value="${value%\'}"
    value="${value#\'}"
    # Export if it's the key we need
    if [ "$key" = "PARCEL_API_KEY" ]; then
      export PARCEL_API_KEY="$value"
      break
    fi
  done < "$ENV_FILE"
fi

# Fall back to keychain if .env didn't provide the key
if [ -z "$PARCEL_API_KEY" ]; then
  export PARCEL_API_KEY=$(security find-generic-password -s "env/PARCEL_API_KEY" -w 2>/dev/null)
fi

# Final check
if [ -z "$PARCEL_API_KEY" ]; then
  echo "Error: PARCEL_API_KEY not found" >&2
  echo "" >&2
  echo "Option 1 (recommended): Create $ENV_FILE with:" >&2
  echo "  PARCEL_API_KEY=your_api_key_here" >&2
  echo "" >&2
  echo "Option 2: Add to macOS Keychain:" >&2
  echo "  security add-generic-password -s 'env/PARCEL_API_KEY' -a '\$USER' -w 'YOUR_API_KEY'" >&2
  exit 1
fi

# Use the pre-bundled server (includes all dependencies, no node_modules needed)
exec node "$SCRIPT_DIR/../mcp-server/parcel/bundle/server.mjs" "$@"
