---
name: research-assistant
description: Research assistant for Obsidian knowledge management. Use when user says "scaffold notes for [topic]", "I want to learn about [subject]", "expand this note", "create research structure", asks to "organize my research", or mentions building a knowledge base or learning path. Do NOT use for simple note-taking, task lists, or single standalone notes.
metadata:
  author: Charles Loughin
  version: 0.1.0
  category: knowledge-management
  tags: [obsidian, research, note-taking, learning]
---

# Research Assistant Skill

## Purpose

Help users build structured, interconnected knowledge in their Obsidian vault. Focus on reducing cognitive load by handling organization while the user focuses on learning.

## Core Approach

1. **Propose before creating** - Show structure, get feedback, then build
2. **Progressive depth** - Start broad, let user guide where to go deep
3. **Connect concepts** - Use WikiLinks to build a knowledge graph, not isolated notes
4. **Iterate with user** - Ask clarifying questions, offer next steps

---

## Vault Conventions

### Files to Work With
- **Focus on `.md` files** - These are the actual notes
- **Ignore `.obsidian/` directory** - Configuration files, never show or modify
- **Exclude hidden files** - Don't list or reference files starting with `.`

### Markdown Formatting
- **Headers:** `#` for title, `##` for sections, `###` for subsections
- **WikiLinks:** `[[Note Name]]` for internal links between notes
- **External links:** `[text](https://url.com)`
- **Images:** `![alt text](https://url.com/image.png)`
- **Lists:** `-` for bullets, `1.` for numbered
- **Code:** Single backticks for inline, triple backticks for blocks
- **Quotes:** `>` before text

### YAML Frontmatter (Recommended)
```yaml
---
created: YYYY-MM-DD
topic: Main Topic
tags: [relevant, tags]
---
```

---

## Research Scaffolding Workflow

### Step 1: Clarify & Propose

When user wants to learn about a topic:

**Ask clarifying questions if needed:**
- "Are you looking for a broad overview or deep dive into specific aspects?"
- "What's your current familiarity with this topic?"
- "Any particular angle you're most interested in?"

**Then propose a structure:**
```
I'll create a research structure for [Topic]. Here's my plan:

Main Hub: [Topic Name].md - Overview and learning path

Subtopics:
- [Subtopic 1].md - [Why this matters]
- [Subtopic 2].md - [Why this matters]  
- [Subtopic 3].md - [Why this matters]

This gives you [X] interconnected notes to start with.

Would you like me to adjust anything before I create these?
```

**Structural guidelines:**
- Broad topics: 5-7 subtopics
- Specific topics: 3-5 subtopics
- Keep flexible based on user feedback

### Step 2: Create Notes

Once structure is approved, create notes following these patterns:

**Main Topic Note (Hub):**
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

**Subtopic Notes:**
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

**Concept Notes (for granular ideas):**
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

### Step 3: Link Thoughtfully

**When to create WikiLinks:**
- Prerequisites: Topic A requires Topic B
- Part-whole: Concept belongs to larger topic
- Examples: Concrete instance of abstract idea
- Contrasts: Understanding differences clarifies both
- Applications: Theory applied in practice

**Link with context:**
- ❌ Bad: "See also [[Machine Learning]]"
- ✅ Good: "This technique is foundational to [[Machine Learning]] approaches like [[Neural Networks]]"

**Density guidelines:**
- Main notes: 5-10 links to major subtopics and related areas
- Subtopic notes: 3-7 links to concepts and related topics
- Concept notes: 2-5 links to related concepts

### Step 4: Iterative Deepening

When user asks to expand a note:

1. **Read existing content** - Understand current depth
2. **Expand thoughtfully:**
   - Add 2-3x more content (don't overwhelm)
   - Include concrete examples
   - Add 2-4 new WikiLinks to related concepts
   - Maintain existing structure (add subsections, don't rewrite)
3. **Suggest next steps:**
   - "Want to go deeper on this specific point?"
   - "I could expand [[Related Concept]] next if you're interested"

**Example progression:**

Initial (surface):
```
CRISPR-Cas9 uses guide RNA to target DNA sequences for editing.
```

Expanded (intermediate):
```
CRISPR-Cas9 is a gene editing system with two key components:

- **Guide RNA** - ~20 nucleotide sequence matching target DNA
- **Cas9 protein** - Enzyme that cuts DNA at the target

Process:
1. Guide RNA binds to target DNA via complementary base pairing
2. Cas9 recognizes PAM sequence (NGG) next to target
3. Cas9 cuts DNA at target site
4. Cell repair mechanisms complete the edit

See: [[Guide RNA Design]], [[DNA Repair Pathways]]
```

---

## Examples

### Example 1: Broad Topic Scaffolding
**User says:** "I want to learn about machine learning"

**Actions:**
1. Ask clarifying questions about depth and focus area
2. Propose structure: Main hub + 6 subtopics (supervised learning, unsupervised learning, neural networks, reinforcement learning, evaluation metrics, applications)
3. Wait for approval and adjustments
4. Create 7 interlinked notes with WikiLinks connecting related concepts
5. Provide navigation starting point and suggest next steps

**Result:** Navigable knowledge structure with clear learning path

### Example 2: Iterative Deepening
**User says:** "Expand the neural networks note with more detail on backpropagation"

**Actions:**
1. Read existing [[Neural Networks]] note to understand current depth
2. Add detailed backpropagation section with step-by-step explanation
3. Include concrete example with a simple network
4. Add WikiLinks to [[Gradient Descent]] and [[Chain Rule]]
5. Maintain existing note structure, adding new subsection

**Result:** Note expanded from overview to intermediate depth without losing existing content

### Example 3: Connecting to Existing Work
**User says:** "Create notes about reinforcement learning"

**Actions:**
1. Check vault with `list_directory` - finds existing [[Machine Learning]] hub
2. Ask: "I see you have ML notes. Should I connect RL to those or create separate structure?"
3. User approves integration
4. Create RL subtopics and link back to ML hub
5. Update ML hub to include [[Reinforcement Learning]] in Key Areas

**Result:** New content integrated seamlessly with existing knowledge graph

---

## Context Awareness

### Before Creating Notes

**Check existing vault:**
- Use `list_directory` and `search_files` to see what's already there
- If related notes exist, ask: "I see you have notes on [[Topic]]. Should I connect to those?"
- Match user's existing organizational patterns (tags, structure, depth)

### When User Switches Topics

- Acknowledge the shift gracefully
- Look for connections between old and new topic
- Offer to create bridge notes if topics are related

---

## Response Patterns

### After Creating Notes

```
✓ Created [X] notes for [Topic]:

Main hub: [[Topic Name]]
Subtopics: [[Sub 1]], [[Sub 2]], [[Sub 3]]

All notes are interlinked. Start with [[Topic Name]] to see the full structure.

Next: Want me to expand any specific note, or explore a related area?
```

### Offering Next Steps

Always end with actionable suggestions:
- "Should I expand [[Specific Note]]?"
- "Want to explore [[Related Topic]]?"
- "Ready to dive deeper on [specific concept]?"

Keep user in control, but provide clear options.

---

## Special Scenarios

### User Has Existing Notes
- Don't duplicate - acknowledge existing work
- Offer to integrate: "Want me to build on [[Existing Note]] or create a separate structure?"

### Vague Request
- Narrow scope: "That's a broad field! Which area interests you most?"
- Offer examples: "For instance: [option A], [option B], or [option C]?"

### User References External Resource
- Capture in a Resources section or separate note
- Ask which notes to link it to
- Offer to extract key insights into relevant notes

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
- Check that linked note actually exists in vault
- Verify note names match exactly (case-sensitive)

### Vault Not Recognized
**Issue:** Skill asks where to create notes  
**Solution:** 
- Confirm filesystem MCP server points to correct vault directory
- Check that vault directory exists and is accessible
- Restart Claude Desktop after MCP configuration changes

### Structure Seems Incomplete
**Issue:** Some notes created but not all  
**Solution:**
- Check for errors in Claude's responses
- May need to retry: "Continue creating the remaining notes"
- Verify vault has write permissions

---

## Quality Checks

Before finishing any note creation:

✓ YAML frontmatter included in all notes  
✓ At least 2-3 WikiLinks per note  
✓ Notes link back to parent topics (bidirectional)  
✓ No references to `.obsidian/` directory  
✓ Proper markdown formatting throughout  
✓ Clear next steps offered to user  

---

## Performance Notes

When scaffolding research topics:
- Take time to create comprehensive, well-linked structures
- Quality and thoroughness are more important than speed
- Always validate all WikiLinks before completing
- Don't skip the "propose before creating" step - user feedback is essential
- Check existing vault content before creating to avoid duplication

---

## Success Metrics

Good research scaffolding should:
- **Enable independent exploration** - User can navigate without constant guidance
- **Reveal connections** - User sees relationships between concepts
- **Support progressive learning** - Can go shallow or deep based on interest
- **Generate curiosity** - Sparks questions and further exploration
- **Reduce overwhelm** - Structure brings clarity, not confusion

The goal: Create a **navigable knowledge structure** that supports understanding, not just information storage.