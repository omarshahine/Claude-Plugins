---
description: |
  Generate reading digest HTML from summarized email data. Use when:
  - Batch processor has created summarized items in reading-digest-state.yaml
  - User wants to view their reading digest

  <example>
  user: "Show my reading digest"
  assistant: "I'll generate the reading digest HTML from your summarized emails."
  </example>
model: sonnet
color: indigo
tools: "*"
---

# Reading Digest Generator

Generate a newspaper-style HTML digest from AI-summarized emails stored in reading-digest-state.yaml.

**CRITICAL RULES**:
- You MUST use the existing HTML template. NEVER write HTML, CSS, or JavaScript yourself.
- You ONLY produce a JSON data file, then use a script to inject it into the template.
- The template contains ALL the UI logic (cards, radio buttons, modals, etc.)

## Step 1: Read State File

```
Read: ~/.claude/data/chief-of-staff/reading-digest-state.yaml
```

If file doesn't exist or has no items → STOP. Report: "No items in reading digest. Use `/chief-of-staff:batch` and mark emails as 'Summarize' first."

## Step 2: Find Template

```
Glob: ~/.claude/plugins/cache/**/chief-of-staff/**/assets/reading-digest.html
```

If template not found → STOP. Report: "Reading digest template not found. Try reinstalling chief-of-staff plugin."

## Step 3: Read Template

Read the template file and confirm it has the data markers:
- `// BEGIN_DIGEST_DATA`
- `// END_DIGEST_DATA`

## Step 4: Write DIGEST_DATA JSON File

Write a file to `/tmp/digest-data.js` containing ONLY the JavaScript data block.

The file must start with `// BEGIN_DIGEST_DATA` and end with `// END_DIGEST_DATA`.

**Required structure:**

```javascript
    // BEGIN_DIGEST_DATA - Do not remove this marker
    const DIGEST_DATA = {
      generated: "ISO-date",
      sessionId: "digest-YYYY-MM-DD-NNN",
      items: [
        {
          emailId: "email-id",
          from: { name: "Sender Name", email: "sender@example.com" },
          subject: "Email subject",
          receivedAt: "2026-02-15T12:00:00Z",
          summarizedAt: "2026-02-17T10:30:00Z",
          summary: {
            tldr: "One or two sentence summary.",
            keyPoints: ["Point 1", "Point 2", "Point 3"],
            actionItems: ["Action 1"] or [],
            estimatedReadTime: "5 min",
            contentType: "analysis"
          }
        }
      ]
    };
    // END_DIGEST_DATA - Do not remove this marker
```

Copy items directly from reading-digest-state.yaml. Sort by receivedAt (newest first).

## Step 5: Inject Data Into Template

Use this Bash command to combine template + data into the output file:

```bash
python3 -c "
template = open('TEMPLATE_PATH').read()
data = open('/tmp/digest-data.js').read()
start = template.find('    // BEGIN_DIGEST_DATA')
end = template.index('\n', template.find('// END_DIGEST_DATA')) + 1
if start == -1: raise Exception('BEGIN marker not found')
output = template[:start] + data.rstrip() + '\n' + template[end:]
with open('/tmp/reading-digest.html', 'w') as f:
    f.write(output)
print(f'Output: {output.count(chr(10))} lines')
" && open /tmp/reading-digest.html
```

Replace `TEMPLATE_PATH` with the actual path from the Glob result.

**NEVER use the Write tool to write HTML.** Always use this injection script.

## Step 6: Report

```
Reading digest generated with X items.

Items by content type:
- Analysis: X
- News: X
- Tutorial: X
- Update: X
- Opinion: X

Browser opened. Review summaries, pick Archive or Delete for each.
Then run: /chief-of-staff:batch --digest
```

## Errors

| Error | Action |
|-------|--------|
| No state file | STOP. "No reading digest state found." |
| Empty items | STOP. "No items in reading digest." |
| Template not found | STOP. Report paths searched. |
| Markers not found | Use fallback: match `const DIGEST_DATA = {` to `};` before `const decisions` |
