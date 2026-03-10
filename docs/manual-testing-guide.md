# Manual Testing Guide

This guide covers core capabilities for the three Claude Skills in this project. Run tests in a Claude Desktop conversation with the filesystem MCP server connected and the relevant skills loaded.

Each test has: **ID**, **Trigger phrase**, **Expected behavior**, and **Pass criteria**.

---

## Setup Checklist

Before running any tests:

- [ ] Claude Desktop is running
- [ ] Filesystem MCP server is connected (verify in Settings → Developer → MCP Servers)
- [ ] Skills are loaded (verify by asking "Which skills do you have loaded?")
- [ ] Vault path points to `obsidian_vault/` directory in this repo
- [ ] Optional: start with a clean/empty vault for isolated tests

---

## Skill: obsidian-vault

### OV-01: Basic Note Creation

**Trigger:** "Create a note called Test Note with a brief summary of photosynthesis"

**Expected behavior:**
- Note created as `Test Note.md` in the vault root
- Includes YAML frontmatter with `created`, `topic`, and `tags` fields
- Markdown is properly formatted with headers and paragraphs

**Pass criteria:**
- `Test Note.md` exists in vault
- Frontmatter is valid YAML (no syntax errors)
- No raw HTML in the note body
- No `.obsidian/` directory contents referenced

---

### OV-02: WikiLink Formatting

**Trigger:** "Create a note about gravity that links to quantum mechanics and relativity"

**Expected behavior:**
- Both links formatted as `[[Quantum Mechanics]]` and `[[Relativity]]`
- Links are NOT formatted as `[Quantum Mechanics](url)` or `[Quantum Mechanics]`

**Pass criteria:**
- Both links use `[[double bracket]]` WikiLink syntax
- No markdown external link syntax used for internal references

---

### OV-03: Surgical Edit — Append New Section

**Setup:** Ensure `Test Note.md` exists from OV-01 (or another note with content).

**Trigger:** "Add a section on the light-dependent reactions to the Test Note"

**Expected behavior:**
1. Claude calls `read_file` on `Test Note.md` first
2. Claude calls `edit_file` with `dryRun: true` to preview the change
3. Claude reports what will be added and confirms before applying
4. New `## Light-Dependent Reactions` section is appended
5. All existing content above the new section is preserved exactly

**Pass criteria:**
- `edit_file` (not `write_file`) was used for the modification
- Dry run was performed before applying
- Original sections are byte-for-byte identical to pre-edit state
- New section appears at the end of the note

---

### OV-04: Surgical Edit — Modify Specific Section

**Setup:** Ensure `Test Note.md` exists with an Overview section.

**Trigger:** "Update the Overview section in Test Note to also mention chloroplasts"

**Expected behavior:**
1. Claude reads the file first
2. Claude targets only the Overview section with `edit_file`
3. Only the Overview section content changes
4. All other sections are untouched

**Pass criteria:**
- Diff shows only the Overview paragraph changed
- No other sections were reformatted or reordered
- WikiLinks and headings outside the target section are unchanged

---

### OV-05: Vault Navigation — Exclude Config Files

**Trigger:** "What notes do I have in my vault?"

**Expected behavior:**
- Lists `.md` files in the vault
- Does NOT list contents of `.obsidian/` directory
- Does NOT show hidden files (files starting with `.`)

**Pass criteria:**
- Response contains only `.md` filenames
- No configuration files (`.json`, `.css`, plugin files) listed
- No `.obsidian/` path appears in the response

---

## Skill: research-assistant

### RA-01: Topic Scaffolding — Proposal Before Creation

**Trigger:** "I want to learn about quantum computing"

**Expected behavior:**
- Claude asks 1–2 clarifying questions about depth/focus, OR immediately proposes a structure
- Proposal includes a main hub note + 3–7 subtopic notes
- Claude does NOT create any files before receiving user approval

**Pass criteria:**
- No files created in vault at this stage
- Structure clearly presented with hub + subtopics listed
- User is asked to confirm or adjust before creation proceeds

---

### RA-02: Scaffolding Creation After Approval

**Setup:** Following RA-01, a structure has been proposed.

**Trigger:** "That looks good, go ahead and create those"

**Expected behavior:**
- Hub note and all proposed subtopic notes are created
- All notes include YAML frontmatter
- Hub note contains WikiLinks to all subtopics
- Each subtopic note links back to the hub

**Pass criteria:**
- All proposed files exist in vault
- Hub note has WikiLinks to every subtopic
- At least one subtopic has a "Back to [[Hub Name]]" or equivalent link
- Frontmatter is valid YAML in all notes

---

### RA-03: Iterative Deepening — Expand Without Overwriting

**Setup:** At least one subtopic note exists from RA-02.

**Trigger:** "Expand the [subtopic name] note with more detail"

**Expected behavior:**
1. Claude reads the existing note first
2. Claude uses `edit_file` (dry run first, then apply) to add content
3. New content is added without removing any existing content
4. 2–4 new WikiLinks are added
5. Existing structure (headers, sections) is preserved

**Pass criteria:**
- Original content is preserved
- New content added (note is longer than before)
- `edit_file` used, not `write_file`
- No existing sections were removed or reordered

---

### RA-04: Connecting to Existing Notes

**Setup:** Ensure ML-related notes exist in the vault (e.g., from a previous scaffolding session).

**Trigger:** "I want to learn about deep learning"

**Expected behavior:**
- Claude scans the vault and finds existing ML notes
- Claude asks: "I see you have notes on [[Machine Learning]]. Should I connect deep learning to those or create a separate structure?"
- Claude waits for the user's decision before creating anything

**Pass criteria:**
- Existing notes are acknowledged by name
- User is given the explicit choice to connect or keep separate
- No notes created before the user decides

---

### RA-05: Vague Topic Handling

**Trigger:** "I want to learn about science"

**Expected behavior:**
- Claude asks a clarifying question narrowing the scope
- Claude offers 2–3 specific examples ("For instance: physics, biology, chemistry?")
- Claude does NOT immediately propose a structure for "all of science"

**Pass criteria:**
- Clarifying question asked before any structure proposed
- 2+ concrete example areas offered
- No hub/subtopic structure created yet

---

### RA-06: Do Not Activate on Simple Tasks

**Trigger:** "Remind me to call the dentist tomorrow"

**Expected behavior:**
- Claude does NOT create a research scaffold for "calling the dentist"
- Claude either defers to the task-manager skill or asks for clarification about what kind of note the user wants

**Pass criteria:**
- No hub note or subtopic structure created
- Response is appropriate for a task/reminder, not a research topic

---

## Skill: task-manager

### TM-01: Simple Task Creation

**Trigger:** "I need to submit the quarterly report by Friday"

**Expected behavior:**
1. Claude surfaces the intent: "I'll create a task: Submit quarterly report. Due: [next Friday as ISO date]. Anything to adjust?"
2. On confirmation, creates `TaskNotes/Tasks/Submit quarterly report.md`
3. YAML includes correct `due` date in ISO 8601 format, `status: open`

**Pass criteria:**
- File exists at `TaskNotes/Tasks/Submit quarterly report.md`
- `due` field is a valid ISO 8601 date (not "Friday" as a string)
- `status: open` in YAML
- All YAML fields present (blank optional fields retained)

---

### TM-02: Passive Detection Mid-Conversation

**Setup:** Start a conversation about something else (e.g., discussing a research topic).

**Trigger:** Mid-conversation: "Oh by the way I should email Sarah about the contract before next week"

**Expected behavior:**
- Claude pauses the current conversation
- Claude explicitly asks: "Before we move on — it sounds like you want to capture a task: 'Email Sarah about the contract'. Should I create a task note for that?"
- Claude does NOT silently create a task note
- Claude does NOT continue the prior conversation without surfacing this first

**Pass criteria:**
- Explicit offer made before any file is created
- File NOT created until user confirms
- Paraphrase of the task is accurate

---

### TM-03: Natural Language Shorthand

**Trigger:** "Add a task to review the API docs @computer #dev due:2026-03-15"

**Expected behavior:**
- YAML contains `contexts: ["computer"]`
- YAML contains `tags: ["dev"]`
- YAML contains `due: 2026-03-15`

**Pass criteria:**
- All three fields populated correctly from the shorthand
- No shorthand strings appear as literal values in YAML

---

### TM-04: Project Proposal Flow — No Files Yet

**Trigger:** "I want to plan out a project to learn Rust programming"

**Expected behavior:**
- Claude identifies this as a project (multi-step, learning horizon)
- Claude proposes an outline: Goal + task list with 3+ items
- Claude asks for feedback before doing anything else
- No files are created at this stage

**Pass criteria:**
- Project outline proposed with goal and task list
- Explicit question asked about whether the outline looks right
- No files created in vault
- No notes created in `Projects/` or `TaskNotes/Tasks/`

---

### TM-05: Project Refinement and Creation

**Setup:** Following TM-04, the user requests a change to the outline (e.g., "Add a task for setting up the development environment").

**Trigger (part 1):** Request a change to the outline.
**Trigger (part 2):** After seeing the updated outline, say "OK, create it"

**Expected behavior:**
1. Claude incorporates the feedback and re-presents the updated outline
2. On approval, Claude creates `Projects/Learn Rust.md`
3. Claude creates `TaskNotes/Tasks/[Task Name].md` for each task
4. Each task note has `projects: ["[[Learn Rust]]"]` in YAML
5. Project hub lists all tasks as WikiLinks

**Pass criteria:**
- `Projects/Learn Rust.md` exists
- At least one task file in `TaskNotes/Tasks/`
- All task notes have bidirectional `projects` link to hub
- Project hub `## Tasks` section lists WikiLinks to all task notes
- The user's requested change is reflected

---

### TM-06: Priority Inference

**Trigger:** "Add an urgent task to fix the production bug"

**Expected behavior:**
- Task note created with `priority: 1-urgent`

**Pass criteria:**
- `priority: 1-urgent` appears in YAML
- Not `priority: urgent` or `priority: 3-medium`

---

### TM-07: Relative Date Conversion

**Trigger:** "I need to review the report next Monday"

**Expected behavior:**
- `due` field contains an absolute ISO 8601 date (e.g., `2026-03-16`)
- Not the string "next Monday"

**Pass criteria:**
- `due:` field is in `YYYY-MM-DD` format
- Date is the correct calendar date for "next Monday" relative to today

---

### TM-08: Task vs. Research Disambiguation

**Trigger:** "I want to learn about machine learning"

**Expected behavior:**
- Claude routes to research-assistant behavior (proposes a knowledge scaffold)
- Claude does NOT create a task note for "learn about ML"
- If both skills could apply, Claude asks which mode the user wants

**Pass criteria:**
- No task note created in `TaskNotes/Tasks/`
- Research scaffold or clarifying question offered instead

---

## Cross-Skill Tests

### XS-01: Project + Research Integration

**Trigger:** "I'm planning a project to learn Rust. I'll need to research ownership, borrowing, and lifetimes along the way."

**Expected behavior:**
- Claude creates a project structure for "Learn Rust" (`Projects/` + `TaskNotes/Tasks/`)
- Claude creates or proposes a research scaffold for Rust topics
- Project hub note links to the Rust research hub via WikiLink

**Pass criteria:**
- `Projects/Learn Rust.md` exists
- Research notes exist for Rust topics (or a scaffold is proposed)
- At least one WikiLink from the project hub to a research note

---

### XS-02: Task Capture During Research Session

**Setup:** An active research scaffolding conversation is in progress.

**Trigger (mid-session):** "Oh, I should also buy the Rust Programming by Example book"

**Expected behavior:**
- The research conversation is not abandoned
- Claude surfaces: "Before we move on — want me to capture 'Buy Rust Programming by Example book' as a task?"
- If confirmed, task note is created without disrupting the research context
- Research conversation can resume after

**Pass criteria:**
- Task note created in `TaskNotes/Tasks/` (after confirmation)
- Existing research notes are unmodified
- Research context can continue after task is captured

---

## MCP Troubleshooting Tests

### MT-01: MCP Connection Verification

**Trigger:** "List the files in my vault"

**Expected behavior:**
- Claude uses filesystem MCP tools to list `.md` files
- Response shows filenames, not an error

**Pass criteria:**
- Files listed successfully
- No "tool not found" or "MCP server not connected" error

---

### MT-02: Write Permission Check

**Trigger:** "Create a file called Connection Test.md with the text 'MCP is working'"

**Expected behavior:**
- File `Connection Test.md` appears in vault after the command

**Pass criteria:**
- File exists in vault with the expected content
- No permission error returned

---

## Test Log

Use this table to record results for each test run.

| Test ID | Date | Result | Notes |
|---------|------|--------|-------|
| OV-01 | | | |
| OV-02 | | | |
| OV-03 | | | |
| OV-04 | | | |
| OV-05 | | | |
| RA-01 | | | |
| RA-02 | | | |
| RA-03 | | | |
| RA-04 | | | |
| RA-05 | | | |
| RA-06 | | | |
| TM-01 | | | |
| TM-02 | | | |
| TM-03 | | | |
| TM-04 | | | |
| TM-05 | | | |
| TM-06 | | | |
| TM-07 | | | |
| TM-08 | | | |
| XS-01 | | | |
| XS-02 | | | |
| MT-01 | | | |
| MT-02 | | | |
