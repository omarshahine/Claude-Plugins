#!/bin/bash
# Wrapper script to launch Parcel MCP server with API key from macOS Keychain
# This allows secure credential storage without hardcoding secrets

export PARCEL_API_KEY=$(security find-generic-password -s "env/PARCEL_API_KEY" -w 2>/dev/null)

if [ -z "$PARCEL_API_KEY" ]; then
  echo "Error: PARCEL_API_KEY not found in keychain" >&2
  echo "Add it with: security add-generic-password -s 'env/PARCEL_API_KEY' -a '$USER' -w 'YOUR_API_KEY'" >&2
  exit 1
fi

# Get the directory where this script lives, then find the server
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVER_PATH="$SCRIPT_DIR/../mcp-server/parcel/dist/server.js"

exec node "$SERVER_PATH" "$@"
