---
name: task-manager
description: Task and project capture for Obsidian using the TaskNotes plugin. Use when user says "I need to...", "remind me to...", "I should...", "add a task for...", "create a project for...", mentions a deadline or due date in context of something actionable, or wants to brainstorm a multi-step plan or project. Do NOT use for learning or knowledge scaffolding (use research-assistant for that).
metadata:
  author: Charles Loughin
  version: 0.1.0
  category: task-management
  tags: [obsidian, tasks, projects, tasknotes]
---

# Task Manager Skill

## Purpose

Detect when the user wants to capture actionable work and create properly formatted TaskNotes-compatible notes in the Obsidian vault. The user should never need to remember YAML field names or folder paths — Claude handles all of that.

## Vault Operations

- **Task notes** live in `TaskNotes/Tasks/[Task Name].md`
- **Project hub notes** live in `Projects/[Project Name].md`
- All notes follow Obsidian Vault skill formatting conventions
- Use `edit_file` with `dryRun: true` first for all modifications to existing notes

---

## Intent Detection

### Passive Detection Signals

Monitor every message for these signals even when this skill was not explicitly invoked:

**Obligation language:**
- "I need to", "I should", "I have to", "I must", "I want to remember to"

**Delegation language:**
- "remind me", "don't let me forget", "note that I need to", "add a task for"

**Deadline signals:**
- "by [date]", "before [event]", "due [timeframe]", "this week", "next Monday", "end of day"

**Project signals:**
- "I'm planning to", "I want to start a project", "let's plan out", followed by multiple steps or subtasks
- 3+ distinct action items mentioned together
- Multi-session or multi-week scope implied

### Handling Detection Mid-Conversation

When a task or project signal is detected during an ongoing conversation about something else, **pause and ask explicitly before continuing:**

> "Before we move on — it sounds like you want to capture a task: *[paraphrase of the task]*. Should I create a task note for that? If yes, give me any details like due date or priority and I'll create it now."

Do NOT silently create a note. Do NOT continue the conversation without surfacing the intent first.

### Natural Language Shorthand

Users may use shorthand notation. Parse these automatically:

| Shorthand | Maps to YAML field |
|-----------|-------------------|
| `@home`, `@work`, `@computer` | `contexts: ["home"]` |
| `+ProjectName` | `projects: ["[[ProjectName]]"]` |
| `#tag` | `tags: ["tag"]` |
| `due:2026-03-15` or "due Friday" | `due: 2026-03-15` |
| "urgent", "high priority" | `priority: 1-urgent` or `priority: 2-high` |

Convert all relative dates ("next Friday", "in 3 days", "end of week") to ISO 8601 format based on today's date before writing to YAML.

---

## Task Workflow

### Simple Task

A single, clear action item with no subtasks.

1. Detect task intent
2. Surface and confirm in one message:
   > "I'll create a task: *[title]*. Due: *[date if mentioned]*. Priority: *[inferred or ask]*. Anything to adjust?"
3. On confirmation, create `TaskNotes/Tasks/[Task Name].md`
4. Report back: "Task created: [[Task Name]]"

Do not engage in multi-turn refinement for simple tasks. One confirm-and-create.

### Complex Task (with subtasks)

When a task has multiple steps or unclear scope:

1. Ask: "This sounds like it might have a few steps. Should I break it into subtasks, or keep it as one task?"
2. If subtasks: create one parent task note + individual task notes for each subtask; link them via the `projects` field pointing to the parent
3. If single: proceed as simple task

---

## Project Workflow

### Detection Signals

A request is a **project** (not a task) when it has:
- 3 or more distinct action items
- A multi-session or multi-week horizon
- Explicit use of "project", "plan", "roadmap", or "phases"
- Milestones, collaborators, or dependencies mentioned

### Iterative Refinement

Projects require back-and-forth before any notes are created.

1. Detect project intent
2. Propose a lightweight outline:

```
Here's a project outline for [Name]:

Goal: [inferred goal in one sentence]

Tasks:
- [ ] [Task 1] — [brief description]
- [ ] [Task 2] — [brief description]
- [ ] [Task 3] — [brief description]

Does this look right? What should I add, remove, or change?
```

3. Incorporate feedback and re-propose if significant changes are needed
4. Continue iterating until the user explicitly approves: "looks good", "go ahead", "create it", etc.

**Do NOT create any notes during the refinement phase.** Notes are created only after explicit user approval.

### Project Note Creation

Once approved:
1. Create `Projects/[Project Name].md` as the project hub
2. Create `TaskNotes/Tasks/[Task Name].md` for each task
3. Each task note's `projects` field links back to the hub: `projects: ["[[Project Name]]"]`
4. Project hub lists all task notes as WikiLinks under `## Tasks`

---

## YAML Templates

### Task Note

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

# [Task Name]

[Optional notes or description about the task]
```

### Project Hub Note

```yaml
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

## Priority Reference

| Value | Meaning |
|-------|---------|
| `1-urgent` | Must do immediately |
| `2-high` | Important, do soon |
| `3-medium` | Normal priority (default) |
| `4-low` | Someday / maybe |

When priority is not specified, default to `3-medium`.

**Inferring priority from language:**
- "urgent", "ASAP", "critical", "blocking" → `1-urgent`
- "important", "high priority", "soon" → `2-high`
- "eventually", "someday", "low priority", "nice to have" → `4-low`

---

## Status Reference

| Value | Meaning |
|-------|---------|
| `open` | Not started (default for new tasks) |
| `in-progress` | Actively working |
| `done` | Complete |
| `completed` | Archived complete |

---

## Date Handling

- Always use ISO 8601 for `due`, `scheduled`, `dateCreated`, and `dateModified`
- `dateCreated` and `dateModified` must include timezone offset: `2026-03-09T14:30:00-05:00`
- When timezone is unknown, use UTC: `2026-03-09T14:30:00Z`
- **Convert all relative dates to absolute ISO 8601 before writing to YAML.** Examples:
  - "next Friday" → `2026-03-13`
  - "end of week" → `2026-03-13` (Friday)
  - "in 3 days" → `2026-03-12`
- If today's date is uncertain, ask the user before computing relative dates

---

## Response Patterns

### After Creating a Task

```
Task created: [[Task Title]]
Due: [date] | Priority: [priority] | Contexts: [contexts if set]
Stored at: TaskNotes/Tasks/[filename]
```

### After Creating a Project

```
Project created: [[Project Name]]
[N] tasks created:
- [[Task 1]]
- [[Task 2]]
- [[Task 3]]

Start with [[Project Name]] to see the full plan.
```

### Mid-Conversation Task Offer

```
Before we move on — it sounds like you want to capture a task: "[paraphrase]".
Should I create a task note for that? If yes, give me any details like due date or priority and I'll create it now.
```

---

## Interaction with Other Skills

When a project involves significant research or learning, **both skills can be active in the same conversation**:

- The **task-manager** skill handles the project structure and task notes
- The **research-assistant** skill handles knowledge scaffolding for the research component
- A project hub note in `Projects/` can WikiLink to a research hub note in the vault root

Example: A "Learn Rust" project could have task notes for each milestone (`TaskNotes/Tasks/`) and link to a `[[Rust Programming]]` research hub note with subtopics.

---

## Quality Checklist

Before completing any task or project creation:

✓ All YAML fields present (blank optional fields retained, not omitted)
✓ `dateCreated` and `dateModified` set to current timestamp with timezone
✓ Task notes stored in `TaskNotes/Tasks/`
✓ Project hub notes stored in `Projects/`
✓ Each task note's `projects` field links back to the project hub (for project tasks)
✓ Project hub lists all task notes as WikiLinks under `## Tasks`
✓ User explicitly confirmed project structure before creation
✓ Relative dates converted to ISO 8601 absolute dates
