---
name: task-manager
description: Task, project, and calendar capture for Obsidian and Google Calendar. Use when user says "I need to...", "remind me to...", "block time for...", "schedule a meeting...", "I should...", "add a task for...", "create a project for...", mentions a deadline or due date, or wants to brainstorm a multi-step plan or project. Do NOT use for learning or knowledge scaffolding (use research-assistant for that).
metadata:
  author: Charles Loughin
  version: 0.2.0
  category: task-management
  tags: [obsidian, tasks, projects, tasknotes, google-calendar]
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
| "urgent", "high priority" | `priority: high` |

Convert all relative dates ("next Friday", "in 3 days", "end of week") to ISO 8601 format based on today's date before writing to YAML.

---

## Intent Triage — Task vs. Reminder vs. Calendar Event

Every actionable request must be routed before any note or event is created. Use this decision table. When multiple signals apply, use the highest row that matches.

| Signal | Route |
|--------|-------|
| "block [duration] for", "reserve time for", "set aside [duration]" | **Calendar event** (time block, no task note unless asked) |
| "meeting / call / appointment at [time]" | **Calendar event** + optional TaskNote |
| "remind me at [time]", "alert me at", "ping me at" | **Calendar reminder** (timed notification; no duration block) |
| Deadline + specific clock time ("by 3pm Thursday") | **TaskNote** + **Calendar reminder** at that time |
| "I need to / I should / I have to" + no specific time | **TaskNote only** |
| "someday", "eventually", "low priority", no date | **TaskNote only** (priority: low) |
| 3+ action items, multi-week scope, "project" | **Project workflow** (see Project Workflow section) |

**When in doubt between reminder and event:** a reminder is a notification at a point in time with no duration; an event occupies a block of time on the calendar. "Remind me to call the dentist at noon" → reminder. "Block an hour for the dentist at noon" → event.

**Confirmation before routing:** Always confirm the route with the user before creating anything:
> "I'll create a TaskNote for this with a due date of Thursday and a calendar reminder at 3pm. Does that sound right?"

Do not silently create calendar events — they appear on a shared or visible calendar and cannot always be undone cleanly.

---

## Natural Language Time Parsing

Convert all time expressions to absolute values before creating any note or event. Never write relative strings ("next Friday", "tomorrow") into YAML or calendar fields.

### Date Expressions

| Expression | Resolution rule |
|------------|----------------|
| "today" | Current date (YYYY-MM-DD) |
| "tomorrow" | Current date + 1 day |
| "next [weekday]" | The named weekday in the next calendar week (not the current week, even if that day is still ahead) |
| "this [weekday]" | The named weekday in the current calendar week |
| "this weekend" | The nearest Saturday |
| "end of week" / "EOW" | Friday of the current week |
| "end of month" / "EOM" | Last calendar day of the current month |
| "in [N] days" | Current date + N days |
| "in [N] weeks" | Current date + N×7 days |

### Time-of-Day Expressions

| Expression | Resolution rule |
|------------|----------------|
| "morning" | 09:00 local time |
| "afternoon" | 14:00 local time |
| "evening" | 18:00 local time |
| "end of day" / "EOD" / "COB" | 17:00 local time |
| "noon" / "midday" | 12:00 |
| "midnight" | 00:00 (next calendar day if "by midnight tonight") |

### Combined Examples

| User says | Resolves to |
|-----------|-------------|
| "by Thursday EOD" | due: [Thursday's date], reminder at 17:00 Thursday |
| "next Monday morning" | scheduled: [next Monday], time: 09:00 |
| "in 3 days at 2pm" | date: [current date + 3], time: 14:00 |
| "this Friday by noon" | due: [this Friday], reminder at 12:00 Friday |
| "end of next week" | due: [Friday of next week] |
| "COB tomorrow" | due: [tomorrow], reminder at 17:00 tomorrow |

**If today's date is uncertain:** ask the user before computing any relative date. Do not guess.

**Timezone:** Use the user's local timezone unless they specify otherwise. If timezone is unknown, use the system timezone and note it in the task details.

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
priority: normal
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
| `high` | Important, do soon or immediately |
| `normal` | Default priority |
| `low` | Someday / maybe |

When priority is not specified, default to `normal`.

**Inferring priority from language:**
- "urgent", "ASAP", "critical", "blocking", "important", "soon" → `high`
- "eventually", "someday", "low priority", "nice to have" → `low`

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

## Google Calendar Integration

When the intent triage routes to a calendar event or reminder, use the Google Calendar MCP tools. These tools are separate from the TaskNotes MCP — they operate on Google Calendar, not Obsidian.

### Available Operations

| Goal | Tool to call |
|------|-------------|
| Create a timed event or reminder | `create_event` with title, start datetime, end datetime |
| Check for conflicts / find open slots | `suggest_time` for the target time range |
| Read an existing event | `get_event` by event ID |
| Update an existing event | `update_event` by event ID |
| List upcoming events | `list_events` with time range |
| RSVP to an invitation | `respond_to_event` |
| Remove an event | `delete_event` |
| See which calendars are available | `list_calendars` |

### Event Creation Workflow

1. **Confirm the route** with the user (see Intent Triage section)
2. **Check for conflicts** — call `suggest_time` for the target time window before creating
3. **Create the TaskNote first** (if applicable) — get the vault path back from `tasknotes_create_task`
4. **Create the calendar event** — call `create_event`; include the vault path in the event description for bidirectional linking
5. **Update the TaskNote** — use `edit_file` to add the calendar event ID to the note's frontmatter

### Bidirectional Linking Convention

**In the TaskNote frontmatter:**
```yaml
calendar_event_id: [event ID returned by create_event]
```

**In the calendar event description:**
```
Linked note: TaskNotes/Tasks/[filename].md
```

This links both artifacts so either one surfaces the other. The TaskNote is always created first — if calendar creation fails, the TaskNote still exists with a note that linking failed.

### Failure Handling

- **If TaskNote creation succeeds but calendar creation fails:** report what happened; do not roll back the TaskNote. Add a `calendar_event_id: pending` field to the note so the user knows to retry.
- **If conflict detected:** report the conflict and ask whether to proceed, reschedule, or skip the calendar step.
- **If Calendar MCP is unreachable:** create the TaskNote only; report that the calendar step was skipped.

### Response Pattern After Creating Both

```
TaskNote created: [[Task Title]]
Calendar event created: [Event Title] on [Date] at [Time]–[End Time]
Both are linked — the note references the event ID, the event links back to the note.
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

✓ Intent triage completed — route confirmed with user before creating anything
✓ All YAML fields present (blank optional fields retained, not omitted)
✓ `dateCreated` and `dateModified` set to current timestamp with timezone
✓ Task notes stored in `TaskNotes/Tasks/`
✓ Project hub notes stored in `Projects/`
✓ Each task note's `projects` field links back to the project hub (for project tasks)
✓ Project hub lists all task notes as WikiLinks under `## Tasks`
✓ User explicitly confirmed project structure before creation
✓ Relative dates converted to ISO 8601 absolute dates
✓ For calendar events: `suggest_time` conflict check run, TaskNote created before `create_event`, bidirectional linking set
