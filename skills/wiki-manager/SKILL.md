---
name: wiki-manager
description: LLM Wiki pattern for persistent, compounding knowledge management in Obsidian. Use when the user says "ingest", "add this to my wiki", "what does my wiki say about", "query the wiki", "lint the wiki", or drops a file in raw/ and asks Claude to process it. Do NOT use for one-off research scaffolding (use research-assistant for that) or task creation (use task-manager).
metadata:
  author: Charles Loughin
  version: 0.1.0
  category: knowledge-management
  tags: [obsidian, wiki, ingest, query, lint, llm-wiki]
---

# Wiki Manager Skill

## Purpose

Maintain a persistent, compounding knowledge base in the Obsidian vault. Unlike research-assistant (which scaffolds notes on demand), this skill treats the vault's `wiki/` directory as a living document store that grows richer with every source added and every question answered.

The key invariant: **knowledge accumulates**. Every ingest updates the wiki. Every answered query can be filed as a synthesis page. The wiki is never just a cache — it is a curated, cross-linked knowledge artifact.

---

## CRITICAL: Read SCHEMA.md First

> **At the start of every wiki session, read `SCHEMA.md` from the vault root.**
> It is the authoritative spec for page types, frontmatter conventions, cross-reference format,
> and directory layout. Do not rely on this skill file alone — SCHEMA.md may have evolved
> since this skill was written, and it takes precedence on any convention conflict.

If `SCHEMA.md` does not exist yet, follow the bootstrap procedure in the **Setup** section below.

---

## Vault Directory Structure

```
vault/
  raw/               # immutable source documents — user writes, Claude reads only
  wiki/
    index.md         # content catalog: link + one-line summary per page
    log.md           # append-only chronological log of all wiki operations
    entities/        # people, organizations, places
    concepts/        # ideas, frameworks, definitions
    sources/         # one summary page per ingested raw source
    synthesis/       # analyses, comparisons, filed query results
  SCHEMA.md          # wiki conventions; co-evolved by user and Claude
```

**Directory rules:**
- `raw/` is read-only from Claude's perspective. Never modify or delete files there.
- `wiki/index.md` and `wiki/log.md` must always exist once the wiki is initialized.
- New pages go into the appropriate subdirectory, never directly in `wiki/`.
- `SCHEMA.md` lives in the vault root (alongside `raw/` and `wiki/`), not inside `wiki/`.

---

## Setup: First-Time Initialization

When a user asks to set up the wiki for the first time (no `wiki/` directory exists yet):

1. Create the directory structure (all subdirs)
2. Create `wiki/index.md` with the standard header (see template below)
3. Create `wiki/log.md` with the standard header
4. Create `SCHEMA.md` from the template below
5. Report: "Wiki initialized. Drop source files into `raw/` and say 'ingest [filename]' to begin."

Do not create any wiki content pages during setup — only the structural files.

---

## Phase 1: Ingest

### When to Invoke

The user says one of:
- "Ingest [filename]"
- "I just added an article to raw/ — please process it"
- "Add this to my wiki"
- "Process the new file in raw/"

### Ingest Workflow

**Step 1 — Read SCHEMA.md**
Always read `SCHEMA.md` first to confirm current conventions before writing any page.

**Step 2 — Read the source**
Read the file from `raw/`. The file may be a markdown export, a web clip, a PDF text extraction, or a plain text document.

**Step 3 — Discuss key takeaways**
Before writing anything, surface the 3–5 most significant claims, findings, or ideas from the source. Ask the user:
- "Here are the key takeaways I found. Anything to add or de-emphasize before I integrate this?"
- This step is a checkpoint, not a lengthy conversation. One exchange is enough unless the user has significant feedback.

**Step 4 — Create the source summary page**
Write `wiki/sources/<slug>.md` where `<slug>` is a kebab-case version of the title.

Use the Source page template from SCHEMA.md. At minimum include:
- YAML frontmatter with `type: source`, `created`, `title`, `source_file` (path in raw/), and `tags`
- A brief summary (3–5 sentences)
- A Key Claims section (bullet list)
- A Cross-References section (WikiLinks to entities and concepts this source informs)

**Step 5 — Update `wiki/index.md`**
Use `edit_file` to add one line to the Sources section of the index:
```
- [[sources/<slug>]] — [one-line summary of what the source is about]
```

**Step 6 — Append to `wiki/log.md`**
Use `edit_file` to append to the end of the file:
```
## [YYYY-MM-DD] ingest | <Title>
Source: raw/<filename>
Created: wiki/sources/<slug>.md
Updated: [list of any other pages updated]
```

**Step 7 — Update related entity and concept pages**
This is the step that makes the wiki compound. For each key entity or concept in the source:
1. Check if a page already exists in `wiki/entities/` or `wiki/concepts/`
2. If yes: use `edit_file` to add a cross-reference on the existing page (see SCHEMA.md for cross-reference format)
3. If no: create a new page using the Entity or Concept template from SCHEMA.md; add it to `wiki/index.md`

Aim to update or create 2–5 entity/concept pages per ingest. Do not update more than 10 per session unless the user explicitly asks.

**Step 8 — Report**
After completing all writes:
```
Ingest complete: [[sources/<slug>]]

Created:
- wiki/sources/<slug>.md

Updated:
- wiki/index.md
- wiki/log.md
- [[concept/entity pages updated, if any]]

[N] total wiki pages now indexed.
```

### Ingest Constraints

- **Never modify files in `raw/`**. They are the immutable record of what was ingested.
- **Always read existing pages before updating them** — use the Surgical Edit Protocol from the obsidian-vault skill.
- **One ingest per session** unless the user explicitly asks for batch processing. Quality over speed.
- **Confirm ambiguous entities** — if a source mentions "Smith" and it's unclear which Smith, ask before linking to a specific entity page.

---

## Phase 2: Query

### When to Invoke

The user asks a question about accumulated knowledge:
- "What does my wiki say about [topic]?"
- "How does [concept A] relate to [concept B]?"
- "Summarize what I know about [entity]"
- "What have I read about [topic]?"

### Query Workflow

**CRITICAL: Never answer a question from memory. Always navigate the wiki first.**

1. **Read `wiki/index.md`** — identify which pages are relevant to the question
2. **Read relevant pages** — drill into entity, concept, and source pages as needed
3. **Synthesize** — compose an answer with explicit citations to specific wiki pages: `([[Concept Page]])`
4. **Offer to file** — if the synthesis is non-trivial (more than a one-liner), offer:
   > "This synthesis might be worth keeping. Want me to file it as `wiki/synthesis/<slug>.md`?"
5. **File if approved** — create the synthesis page; update index and log

The query workflow is **read-only by default**. Only write if the user approves filing.

---

## Phase 3: Lint

### When to Invoke

The user asks for a wiki health check:
- "Lint the wiki"
- "What needs attention in my wiki?"
- "Find gaps in my wiki"
- "Health check my notes"

### Lint Checks

Run these checks in order and report results as a prioritized list:

**Check 1 — Orphan pages**
Pages in `wiki/` subdirectories that have no inbound links from `wiki/index.md` or other wiki pages. These may be forgotten or miscategorized.

**Check 2 — Missing concept pages**
Concept names that appear as WikiLinks in 2+ pages but have no dedicated page in `wiki/concepts/`. These are candidates for new pages.

**Check 3 — Stale source references**
Source pages in `wiki/sources/` whose `source_file` path no longer exists in `raw/`. The raw file may have been moved or deleted.

**Check 4 — Index gaps**
Pages in `wiki/` subdirectories that exist on disk but are not listed in `wiki/index.md`.

**Check 5 — Empty or stub pages**
Pages with no Key Claims, no cross-references, or fewer than 3 bullet points. These need expansion.

### Lint Report Format

```
Wiki Lint Report — [YYYY-MM-DD]

Issues found: [N]

HIGH
- Orphan: [[page]] — no inbound links
- Missing concept: "Term" — appears in [[page A]], [[page B]]

MEDIUM
- Index gap: wiki/concepts/foo.md not in index.md

LOW
- Stub: [[page]] — fewer than 3 key claims

Suggested next actions:
- [specific, actionable suggestion per issue]
```

Do not automatically fix lint issues. Present the report and let the user decide what to act on.

---

## SCHEMA.md Template

Use this template when initializing the wiki for the first time. The user and Claude co-evolve this file over time — update it when conventions change, and always read it at session start.

```markdown
---
version: 1.0
updated: YYYY-MM-DD
---

# Wiki Schema

This file defines the conventions for the wiki layer of this Obsidian vault.
It is the authoritative reference for page types, frontmatter, cross-references,
and directory layout. Claude reads this at the start of every wiki session.

## Directory Layout

| Directory | Contents |
|-----------|----------|
| raw/ | Immutable source documents; Claude reads but never modifies |
| wiki/sources/ | One summary page per ingested source |
| wiki/concepts/ | Ideas, frameworks, definitions |
| wiki/entities/ | People, organizations, places |
| wiki/synthesis/ | Filed query results and analyses |
| wiki/index.md | Content catalog |
| wiki/log.md | Append-only operation log |

## Page Types and Frontmatter

### Source Page
Frontmatter:
  type: source
  created: YYYY-MM-DD
  title: [Article or document title]
  source_file: raw/[filename]
  tags: [list of relevant tags]

### Concept Page
Frontmatter:
  type: concept
  created: YYYY-MM-DD
  topic: [Concept name]
  tags: [list]

### Entity Page
Frontmatter:
  type: entity
  created: YYYY-MM-DD
  name: [Entity name]
  entity_type: [person | organization | place]
  tags: [list]

### Synthesis Page
Frontmatter:
  type: synthesis
  created: YYYY-MM-DD
  question: [The query that generated this synthesis]
  tags: [list]

## Cross-Reference Format

When adding a cross-reference on an existing page, append to a ## Sources section:
- [[sources/slug]] — [one sentence explaining what this source adds to this page]

## WikiLink Conventions

- Use [[wiki/concepts/slug]] for concept links
- Use [[wiki/entities/slug]] for entity links
- Use [[wiki/sources/slug]] for source links
- Short names ("[[Attention Mechanisms]]") are acceptable when unambiguous

## Index Format

wiki/index.md is organized by page type. Each entry is one line:
- [[path/to/page]] — [one-line description]

## Log Format

wiki/log.md entries use this parseable prefix:
## [YYYY-MM-DD] operation | Title

Where operation is one of: ingest | query | lint | edit | create
```

---

## wiki/index.md Template

```markdown
---
type: wiki-index
updated: YYYY-MM-DD
---

# Wiki Index

## Sources
<!-- One line per ingested source: [[sources/slug]] — summary -->

## Concepts
<!-- One line per concept page: [[concepts/slug]] — summary -->

## Entities
<!-- One line per entity page: [[entities/slug]] — summary -->

## Synthesis
<!-- One line per synthesis page: [[synthesis/slug]] — summary -->
```

---

## wiki/log.md Template

```markdown
---
type: wiki-log
---

# Wiki Log

Append-only log of all wiki operations. Most recent entries are at the bottom.
```

---

## Page Templates

### Source Page

```markdown
---
type: source
created: YYYY-MM-DD
title: [Article or document title]
source_file: raw/[filename]
tags: []
---

# [Article Title]

## Summary
[3–5 sentence summary of what the source is about and why it matters]

## Key Claims
- [Most important claim or finding]
- [Second claim]
- [Third claim]
- [Additional claims as needed]

## Cross-References
- [[concepts/slug]] — [how this source informs this concept]
- [[entities/slug]] — [what this source says about this entity]

## Notes
[Optional: caveats, methodology concerns, things to follow up on]
```

### Concept Page

```markdown
---
type: concept
created: YYYY-MM-DD
topic: [Concept Name]
tags: []
---

# [Concept Name]

## Definition
[Clear, concise definition in 1–2 sentences]

## Key Points
- [Important aspect]
- [Another aspect]
- [Third aspect]

## Sources
<!-- Cross-references added here during ingest -->

## Related
- [[concepts/related-concept]] — [how they relate]
```

### Entity Page

```markdown
---
type: entity
created: YYYY-MM-DD
name: [Entity Name]
entity_type: [person | organization | place]
tags: []
---

# [Entity Name]

## Overview
[2–3 sentences: who/what this entity is and why it appears in the wiki]

## Sources
<!-- Cross-references added here during ingest -->

## Related
- [[entities/related-entity]] — [relationship]
```

### Synthesis Page

```markdown
---
type: synthesis
created: YYYY-MM-DD
question: [The query that generated this]
tags: []
---

# [Descriptive Title of the Synthesis]

## Question
[The question that prompted this synthesis]

## Answer
[The synthesized answer, with inline citations: ([[concepts/slug]])]

## Sources Consulted
- [[sources/slug]] — [what it contributed]

## Open Questions
- [Questions this synthesis raised but did not answer]
```

---

## Interaction with Other Skills

- **obsidian-vault skill** governs all file operations: YAML frontmatter rules, WikiLink format, the Surgical Edit Protocol (`edit_file` with dry run). Always follow it for any write operation.
- **research-assistant skill** creates on-demand scaffolding for topics. If a research scaffold is created for a topic already in the wiki, offer to link the scaffold back to the wiki's concept or entity pages.
- **task-manager skill** is independent of the wiki. Task notes live in `TaskNotes/Tasks/`, never in `wiki/`.

---

## Quality Checklist

Before completing any wiki operation:

✓ SCHEMA.md was read at session start
✓ All new pages have YAML frontmatter with correct `type` field
✓ wiki/index.md updated with new entries
✓ wiki/log.md appended with timestamped entry
✓ Surgical Edit Protocol followed for all modifications to existing pages
✓ Cross-references added on entity/concept pages for each ingest
✓ Source files in raw/ untouched
✓ No wiki content created without user confirmation of key takeaways (Ingest Step 3)
