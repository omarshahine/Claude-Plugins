# Bugbot Rules for Agent-Plugins

## PII and Personal Path Detection

If a file contains paths matching `/Users/[username]/` (macOS home directory), then:
- Add a blocking bug: "Hardcoded macOS home directory path detected. Use wildcards or environment variables instead of personal paths."
- Suggest replacing with a wildcard pattern like `~/` or `*/`

If a file contains paths matching `C:\Users\[username]\` (Windows home directory), then:
- Add a blocking bug: "Hardcoded Windows home directory path detected. Use wildcards or environment variables instead of personal paths."

If a file contains what appears to be a personal username in a path (e.g., `/Users/[name]/` or `[name]-agent-plugins`), then:
- Add a blocking bug: "Personal username detected in file. Remove or replace with a generic placeholder or wildcard."

## Marketplace Path Patterns

If a markdown file in `agents/`, `skills/`, or `commands/` contains a hardcoded marketplace path like `.claude/plugins/cache/[specific-name]/` without wildcards, then:
- Add a blocking bug: "Hardcoded marketplace cache path detected. Use wildcard pattern like `~/.claude/plugins/cache/*/plugin-name/` for portability across different users."

## Email Address Detection

If a file contains a personal email address (e.g., user@domain.com), then:
- Add a blocking bug if in an agent, command, skill, or template file: "Personal email address detected. Replace with a placeholder like `user@example.com` or parameterize via settings."
- Add a non-blocking bug if in README, CLAUDE.md, or plugin.json: "Email address detected. Verify this is intentional (e.g., author field) and not personal data leaking."

Allowed email patterns (do NOT flag these):
- `@example.com`, `@example.org` (RFC 2606 reserved)
- `@anthropic.com`
- `@noreply.github.com` (e.g., `username@users.noreply.github.com`)
- `noreply@` addresses
- Email patterns inside code comments explaining what to look for (e.g., `# look for from:user@domain.com patterns`)

Exclude from email checks:
- CHANGELOG.md
- package-lock.json
- node_modules/
- `*.example.yaml` (templates may show format)

## Real Names in Examples and Templates

If an agent, command, skill, or template file in `plugins/` contains real family member names (not generic placeholders) in example output, conversation examples, or sample data, then:
- Add a blocking bug: "Real name detected in example. Replace with generic placeholders (e.g., 'Jane', 'Alex Smith') to avoid leaking personal information."

**Specific patterns to flag** (these are real names that have leaked before):
- First names of family members used in iMessage examples, email examples, or persona signatures
- `[Name]'s AI assistant` where [Name] is a real person's name (use generic like "Jane's AI assistant")
- `Your Name: [real name]` in setup/config examples
- `user_name: [real name]` in YAML config examples
- Real contact names in command usage examples (e.g., `/command send [RealName]`)

Look for:
- Names used in iMessage conversation examples
- Names in email triage examples or sample output
- Names in filing rule examples
- Family member references with real names
- Persona signature examples containing real user names

Allowed exceptions:
- Author name in `plugin.json` author field (this is intentional attribution)
- GitHub username in repository URLs (public identity)
- Marketplace name containing GitHub username (e.g., `omarshahine-agent-plugins`)

## Physical Address Detection

If a file contains what appears to be a real physical/mailing address (street number + street name, or a full address with city/state/zip), then:
- Add a blocking bug: "Physical address detected. Remove or replace with a generic placeholder address (e.g., '123 Main St')."

Look for patterns like:
- `[number] [street name] [Ave|St|Blvd|Dr|Ln|Way|Ct|Rd|Pl|Circle]`
- Full addresses with city, state, zip code

Exclude:
- Generic example addresses (e.g., "123 Main St")
- Documentation explaining address format patterns

## Phone Number Detection

If a file contains US phone number patterns (XXX-XXX-XXXX, (XXX) XXX-XXXX, +1XXXXXXXXXX, or similar), then:
- Add a blocking bug: "Phone number detected. Remove or replace with a placeholder like `555-123-4567`."

Exclude:
- Clearly fake/example numbers (555-XXXX range)
- Regex patterns that match phone numbers (e.g., in validation code)

## API Keys and Secrets

If a file contains patterns like `api_key=`, `token=`, `secret=`, `password=`, `API_KEY`, or `Bearer [token-value]` followed by an actual string value (not a variable reference like `${VAR}`), then:
- Add a blocking bug: "Possible API key or secret detected. Use environment variables instead of hardcoding credentials."

Also flag:
- Hardcoded URLs containing tokens or auth parameters (e.g., `?token=abc123`, `?key=xyz`)
- Base64-encoded strings that look like credentials (long alphanumeric strings assigned to auth variables)
- Cloudflare Access client IDs or secrets

Exclude from secret checks:
- `.env.example` files (these are templates)
- Documentation showing example patterns with clearly fake values
- Variable references like `${API_KEY}` or `process.env.API_KEY`

## Data Files That Should Be Gitignored

If a YAML, JSON, or other data file in a `plugins/*/data/` directory is being added/modified and is NOT an `*.example.yaml`, `*.example.json`, or `.gitignore` file, then:
- Add a blocking bug: "User data file detected in commit. This file should be gitignored. Only `*.example.yaml`, `*.example.json`, and `.gitignore` files should be tracked in `plugins/*/data/` directories."

Specifically watch for these files that contain PII if tracked:
- `settings.yaml` (email provider config, personal names)
- `user-preferences.yaml` (family email addresses, sender lists)
- `filing-rules.yaml` (personal email patterns, family names)
- `delete-patterns.yaml` (personal email patterns)
- `decision-history.yaml` (email triage decisions with real content)
- `interview-state.yaml` (email triage state with real emails)
- `batch-state.yaml` (batch triage state)
- `newsletter-lists.yaml` (subscribed newsletters)
- `fastmail-rules-reference.json` (contains email addresses, physical addresses, family names, email forwarding addresses)
- `checklist.yaml` (credit card benefit usage with personal data)

## Email Forwarding and Service-Specific Addresses

If a file contains email addresses that appear to be service-specific forwarding addresses (e.g., `username@library.readwise.io`, `username@inbox.omnivore.app`, or similar `user-specific-token@service.com` patterns), then:
- Add a blocking bug: "Service-specific email forwarding address detected. These are personal account identifiers and should not be in tracked files."

## Account Numbers and Personal Identifiers

If a file contains what appears to be an account number, member ID, confirmation code, or similar personal identifier (alphanumeric strings that look like account references, especially near keywords like "account", "member", "confirmation", "reservation", "booking"), then:
- Add a non-blocking bug: "Possible account number or personal identifier detected. Verify this is not real account data."

## IP Address Detection

If a file contains an IPv4 address (e.g., `192.168.1.1`) or IPv6 address that is not a well-known example/documentation range, then:
- Add a non-blocking bug: "IP address detected. Verify this is not infrastructure or personal network information."

Allowed IP ranges (do NOT flag):
- `127.0.0.1` and `::1` (localhost)
- `0.0.0.0` (wildcard)
- `192.0.2.x`, `198.51.100.x`, `203.0.113.x` (RFC 5737 documentation ranges)
- `10.x.x.x`, `172.16-31.x.x`, `192.168.x.x` in example/documentation context

## Absolute Paths in Plugin Files

If a markdown file in the `plugins/` directory (in `agents/`, `commands/`, or `skills/`) contains absolute paths starting with `/` or `~` that reference specific user directories or system paths, then:
- Add a non-blocking bug: "Absolute path detected in plugin file. Consider using relative paths, `${CLAUDE_PLUGIN_ROOT}`, or wildcard patterns for portability."

Exclude:
- Paths using `${HOME}` or `${CLAUDE_PLUGIN_ROOT}` variables
- Paths using `~/` as a generic home directory reference
- Well-known system paths (`/usr/`, `/bin/`, `/tmp/`)
- Documentation showing path formats or examples

## Database Path Detection

If a file contains paths to local application databases (e.g., `~/Library/Containers/`, `~/Library/Group Containers/`, `~/Library/Application Support/`) with specific database filenames, then:
- Add a non-blocking bug: "Application database path detected. Verify this does not expose user-specific data structures or locations that could change between users."

## URL Detection with Personal Identifiers

If a file contains URLs that include personal subdomains, account-specific paths, or personal tokens (e.g., `https://username.service.com`, `https://service.com/user/specific-id/`), then:
- Add a non-blocking bug: "URL with possible personal identifier detected. Use environment variables or placeholders for user-specific URLs."

Exclude:
- GitHub URLs with username (public identity, expected in repo/author context)
- URLs using `${VAR}` syntax for variable substitution
- Well-known public URLs

## Global Exclusions

The following file patterns are excluded from ALL checks above:
- `node_modules/` (third-party code)
- `package-lock.json` (auto-generated)
- `*.min.js`, `*.min.css` (minified bundles)
- `bundle/` directories (compiled/bundled code)
- `.git/` directory
