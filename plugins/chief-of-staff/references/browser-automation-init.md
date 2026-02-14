## Browser Automation Initialization (Standard Pattern)

**Some agents need browser automation for web scraping, form filling, or tracking extraction.** The browser backend is configured in settings.yaml.

### Step 1: Read Settings

```
Read: ~/.claude/data/chief-of-staff/settings.yaml
```

Extract:
- `PLAYWRIGHT_MODE` = `providers.playwright.active` (either `"mcp"` or `"cli"`)

If `providers.playwright` is missing from settings.yaml, default to `"mcp"`.

### Step 2a: MCP Mode (`PLAYWRIGHT_MODE = "mcp"`)

Load Playwright MCP tools:
```
ToolSearch query: "+playwright browser"
```

This discovers the available Playwright tools regardless of installation method (plugin-bundled or standalone).

Store the discovered tools as `PLAYWRIGHT_TOOLS`:
- `browser_navigate` - Go to a URL
- `browser_snapshot` - Get page structure (preferred over screenshots)
- `browser_click` - Click elements by ref from snapshot
- `browser_type` - Type into fields
- `browser_fill_form` - Fill multiple form fields
- `browser_close` - Close browser when done

**If no tools found**, display:
```
Playwright MCP not configured. Browser automation unavailable.

Install the Playwright plugin: /plugin install playwright@claude-plugins-official
Or add to chief-of-staff .mcp.json.
```

### Step 2b: CLI Mode (`PLAYWRIGHT_MODE = "cli"`)

Verify the CLI is installed:
```
Bash: which playwright-cli
```

**If not found**, display:
```
playwright-cli not installed. Browser automation unavailable.

Install: brew install nicholasgriffintn/tap/playwright-cli
```

### Step 3: Use via Mapped Approach

**MCP mode** - Call tools directly:
```
PLAYWRIGHT_TOOLS.browser_navigate → url
PLAYWRIGHT_TOOLS.browser_snapshot → get page structure
PLAYWRIGHT_TOOLS.browser_click → click element by ref
PLAYWRIGHT_TOOLS.browser_type → enter text
PLAYWRIGHT_TOOLS.browser_close → close browser
```

**CLI mode** - Call via Bash tool:
```
playwright-cli open <url>        → navigate to URL
playwright-cli snapshot          → get page accessibility tree
playwright-cli click <ref>       → click element by ref
playwright-cli type <ref> <text> → type into element
playwright-cli close             → close browser
```

### Important Notes

- **Always close the browser** when done (both modes) to free resources
- **Prefer `browser_snapshot`** (MCP) or `playwright-cli snapshot` (CLI) over screenshots — returns actionable element refs
- **CLI mode advantages**: Persistent sessions (authenticated sites), headed mode (Cloudflare-protected pages), file downloads
- **MCP mode advantages**: Direct tool integration, no shell overhead, structured responses
