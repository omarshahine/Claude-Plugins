#!/bin/bash
# Agent-Plugins Setup Script
# Run this after cloning to build MCP servers bundled with plugins

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Agent-Plugins Setup"
echo "==================="
echo ""

# Build MCP servers bundled with plugins
echo "Building plugin MCP servers..."

PLUGINS_DIR="$REPO_DIR/plugins"
built_count=0

for plugin_dir in "$PLUGINS_DIR"/*; do
    if [ -d "$plugin_dir/mcp-server" ]; then
        for mcp_dir in "$plugin_dir/mcp-server"/*; do
            if [ -f "$mcp_dir/package.json" ]; then
                mcp_name=$(basename "$mcp_dir")
                plugin_name=$(basename "$plugin_dir")
                echo ""
                echo "  Building $mcp_name MCP server for $plugin_name..."
                (cd "$mcp_dir" && npm install && npm run build) || {
                    echo "  ⚠ Failed to build $mcp_name"
                    continue
                }
                echo "  ✓ $mcp_name built successfully"
                ((built_count++))
            fi
        done
    fi
done

echo ""
if [ $built_count -eq 0 ]; then
    echo "No MCP servers found to build."
else
    echo "Built $built_count MCP server(s)."
fi

echo ""
echo "Setup complete!"
echo ""
echo "To use these plugins, add this marketplace to Claude Code:"
echo "  /plugin marketplace add omarshahine-agent-plugins ~/GitHub/Agent-Plugins"
echo ""
echo "Then install plugins:"
echo "  /plugin install chief-of-staff@omarshahine-agent-plugins"
