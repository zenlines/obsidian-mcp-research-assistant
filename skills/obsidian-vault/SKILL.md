---
name: obsidian-vault
description: Obsidian vault conventions and filesystem operations. Use when creating, reading, editing, or linking notes in the Obsidian vault. Covers formatting rules, YAML frontmatter templates, WikiLink conventions, the surgical edit protocol using edit_file, and MCP troubleshooting. Load alongside any skill that creates or modifies vault files.
metadata:
  author: Charles Loughin
  version: 0.1.0
  category: knowledge-management
  tags: [obsidian, markdown, filesystem, mcp]
---

# Obsidian Vault Skill

## Purpose

Authoritative reference for all Claude interactions with the Obsidian vault via the filesystem MCP server. Every skill that creates or modifies vault files follows these conventions.

---

## Vault Filesystem Conventions

- **Work only with `.md` files** — these are the actual notes
- **Never touch `.obsidian/`** — configuration directory, never show or modify
- **Exclude hidden files** — don't list or reference files starting with `.`
- **Vault root** is the filesystem MCP server root directory

---

## Markdown Formatting Rules

- **Headers:** `#` for title, `##` for sections, `###` for subsections
- **WikiLinks:** `[[Note Name]]` for internal links between notes
- **External links:** `[text](https://url.com)`
- **Images:** `![alt text](https://url.com/image.png)`
- **Lists:** `-` for bullets, `1.` for numbered
- **Code:** Single backticks for inline, triple backticks for blocks
- **Quotes:** `>` before text

---

## YAML Frontmatter Templates

### Research Note

```yaml
---
created: YYYY-MM-DD
topic: Main Topic
tags: [relevant, tags]
---
```

### Task Note (TaskNotes plugin)

All fields must be present. Leave optional fields blank rather than omitting them — the plugin expects the full schema.

```yaml
---
title: [Task Name]
status: open
priority: 3-medium
due: YYYY-MM-DD
scheduled:
dateCreated: YYYY-MM-DDTHH:MM:SS±HH:MM
dateModified: YYYY-MM-DDTHH:MM:SS±HH:MM
contexts: []
projects: []
tags: []
timeEstimate:
recurrence:
reminders:
blockedBy:
---
```

### Project Hub Note

```yaml
---
title: [Project Name]
created: YYYY-MM-DD
tags: [project]
status: active
---
```

---

## WikiLink Conventions

### When to Create Links

Create a WikiLink when the relationship is meaningful for navigation:

- **Prerequisites:** Topic A requires understanding Topic B
- **Part-whole:** Concept belongs to a larger topic
- **Examples:** Concrete instance of an abstract idea
- **Contrasts:** Understanding differences clarifies both concepts
- **Applications:** Theory applied in a specific context

### Link Quality

- ❌ Bad: "See also [[Machine Learning]]"
- ✅ Good: "This technique is foundational to [[Machine Learning]] approaches like [[Neural Networks]]"

Links should carry context — a reader should understand the relationship from the surrounding sentence.

### Density Guidelines

- **Main/hub notes:** 5–10 links to major subtopics and related areas
- **Subtopic notes:** 3–7 links to concepts and related topics
- **Concept notes:** 2–5 links to related concepts

---

## Note Templates

### Hub Note (Main Topic)

```markdown
---
created: YYYY-MM-DD
topic: [Topic Name]
tags: [main-topic]
---

# [Topic Name]

## Overview
[2-3 sentences: what it is, why it matters]

## Key Areas

- **[[Subtopic 1]]** - [One sentence]
- **[[Subtopic 2]]** - [One sentence]
- **[[Subtopic 3]]** - [One sentence]

## Learning Path

[Suggested order for exploring these topics, with reasoning]

## Questions to Explore

- [Open question that emerged]
- [Another direction to consider]

## Related Topics

- [[Related Topic 1]] - [Connection]
```

### Subtopic Note

```markdown
---
created: YYYY-MM-DD
topic: [Main Topic]
tags: [subtopic]
---

# [Subtopic Name]

## Overview
[2-3 sentences in context of main topic]

## Key Points

- **[Important concept]** - [Explanation with [[links]] where relevant]
- **[Another key point]** - [Explanation]
- **[Third point]** - [Explanation]

## Details

[1-2 paragraphs with deeper explanation. Include examples.]

## Related Concepts

- [[Concept A]] - [How it relates]
- [[Concept B]] - [Connection]

## See Also

Back to [[Main Topic Name]]
```

### Concept Note

```markdown
---
created: YYYY-MM-DD
topic: [Main Topic]
tags: [concept]
---

# [Concept Name]

## Definition
[Clear, concise definition]

## Explanation
[2-3 paragraphs with examples]

## Why It Matters
[Connection to bigger picture]

## Related
- [[Related Concept]]
- Part of [[Parent Topic]]
```

### Task Note

```markdown
---
title: [Task Name]
status: open
priority: 3-medium
due: YYYY-MM-DD
scheduled:
dateCreated: YYYY-MM-DDTHH:MM:SS±HH:MM
dateModified: YYYY-MM-DDTHH:MM:SS±HH:MM
contexts: []
projects: []
tags: []
timeEstimate:
recurrence:
reminders:
blockedBy:
---

# [Task Name]

[Optional notes or description about the task]
```

### Project Hub Note

```markdown
---
title: [Project Name]
created: YYYY-MM-DD
tags: [project]
status: active
---

# [Project Name]

## Goal
[What this project accomplishes]

## Tasks
- [ ] [[Task 1]]
- [ ] [[Task 2]]
- [ ] [[Task 3]]

## Notes
[Space for project-level notes, decisions, and context]

## Related
[WikiLinks to related research notes or other projects]
```

---

## Surgical Edit Protocol

When modifying an **existing** note, always use `edit_file` instead of rewriting the whole file with `write_file`. This preserves unrelated content and avoids token waste.

### Step-by-Step

1. **Read the file first** — use `read_file` to get the current content
2. **Run a dry run** — call `edit_file` with `dryRun: true` to preview what will change before applying
3. **Apply the edit** — if the dry run looks correct, call `edit_file` with `dryRun: false` (or omit dryRun)
4. **Never alter content outside the targeted section** — preserve whitespace, casing, and structure of everything else

### Decision Tree

| Intent | `oldText` to target |
|--------|-------------------|
| Add a new section | The last line of the file (append after it) |
| Modify a specific section | That section's `## Header` + its full content block |
| Fix a single fact or sentence | The minimum containing paragraph |
| Fix a WikiLink | The exact surrounding sentence containing the link |

### What NOT to Do

- Do not reformat or reorder unrelated sections during an edit pass
- Do not change heading levels, bullet style, or whitespace outside the target
- Do not use `write_file` for modifications — only use it for **new file creation**

### Example

Expanding the "Overview" section of an existing note:

```
edit_file({
  path: "vault/Neural Networks.md",
  edits: [{
    oldText: "## Overview\nNeural networks are computational models inspired by the brain.",
    newText: "## Overview\nNeural networks are computational models inspired by biological neurons in the brain. They consist of layers of interconnected nodes that transform input data through learned weights.\n\nSee [[Deep Learning]] for modern applications of large-scale neural networks."
  }],
  dryRun: true   // preview first
})
```

---

## Quality Checklist

Before completing any note creation or modification:

✓ YAML frontmatter included in all notes
✓ At least 2–3 WikiLinks per note
✓ Notes link back to parent topics (bidirectional)
✓ No references to `.obsidian/` directory
✓ Proper markdown formatting throughout
✓ `edit_file` used for modifications (not `write_file`)
✓ Clear next steps offered to user

---

## Troubleshooting

### Notes Not Created

**Issue:** Skill loads but files aren't appearing in vault
**Check:**
- Verify filesystem MCP server is connected (Settings > Developer > MCP Servers)
- Confirm vault path is correct in MCP configuration
- Try: "List files in my vault" to verify MCP connection works

### WikiLinks Not Working in Obsidian

**Issue:** Links appear as plain text with brackets
**Solution:**
- Ensure using double brackets: `[[Note Name]]` not `[Note Name]`
- Check that the linked note actually exists in the vault
- Verify note names match exactly (case-sensitive)

### Vault Not Recognized

**Issue:** Skill asks where to create notes
**Solution:**
- Confirm filesystem MCP server points to the correct vault directory
- Check that vault directory exists and is accessible
- Restart Claude Desktop after MCP configuration changes

### Structure Seems Incomplete

**Issue:** Some notes created but not all
**Solution:**
- Check for errors in Claude's responses
- May need to retry: "Continue creating the remaining notes"
- Verify vault has write permissions
