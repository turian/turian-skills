# Best Practices for Writing Skills

> **Contract:** This document is the canonical standard for skills in this repository. All skills must be audited against it. External links are provided only as provenance; this document is the source of truth for this repo.
>
> **Scope Boundary:** This repo provides reusable skills. It does not define your project's policies. If your project has specific conventions, follow that project's `AGENTS.md`.

---

## Standards & Compatibility

This document blends three sources. When they conflict, this section clarifies which rules apply where.

| Standard | Scope | Enforced by CI? |
|----------|-------|-----------------|
| **AgentSkills spec** | Interoperability across agents | Partial (see notes) |
| **Anthropic docs** | Claude Code behavior guidance | No (reference only) |
| **Repo policy** | This repository's conventions | Yes (hard fail) |

### What This Repo's CI Enforces

| Rule | Source | CI Check |
|------|--------|----------|
| Frontmatter: `name` + `description` required | AgentSkills spec | ✓ |
| Frontmatter: optional fields allowed | AgentSkills spec | ✓ |
| Name format: lowercase + numbers + hyphens, 1-64 chars | AgentSkills spec | ✓ |
| Name: no leading/trailing hyphen, no consecutive hyphens | AgentSkills spec | ✓ |
| Name: must match directory name | AgentSkills spec | ✓ |
| Description: max 1024 chars | AgentSkills spec | ✓ |
| Compatibility: max 500 chars (if present) | AgentSkills spec | ✓ |
| Description: must start with "Use when" | **Repo policy** | ✓ |
| Description: must be third-person | **Repo policy** | ✓ |
| DOT diagrams: ≤8 nodes | **Repo policy** | ✓ |
| Required sections: Quick Reference, Failure Modes | **Repo policy** | ✓ |
| Body: min 100 chars | **Repo policy** | ✓ |

### Key Discrepancies

| Topic | AgentSkills Spec | This Repo |
|-------|------------------|-----------|
| Description format | "What it does and when to use it" (flexible) | Must start with "Use when" (strict) |
| Name charset | Unicode lowercase allowed | ASCII lowercase only |
| Required sections | None specified | Quick Reference + Failure Modes |

**Why the stricter rules?** This repo enforces opinionated conventions for consistency. If you're authoring skills for other contexts, the AgentSkills spec is more permissive.

---

**Provenance:** These sources informed this document. You should not need to read them to use this repo.

- [Agent Skills Specification](https://agentskills.io/specification) — Official open format specification
- [Anthropic Official: Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic Official: Claude Code Skills](https://code.claude.com/docs/en/skills)
- [github.com/obra/superpowers](https://github.com/obra/superpowers)
- [github.com/steveyegge/beads](https://github.com/steveyegge/beads)
- [Claude Skills Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

---

## Official Limits & Constraints

These are hard limits from the official Agent Skills specification and Anthropic documentation:

| Field | Limit | Source |
|-------|-------|--------|
| `name` | 64 chars max | Agent Skills spec |
| `name` format | lowercase, numbers, hyphens only | Agent Skills spec |
| `name` restrictions | No start/end hyphen, no consecutive hyphens (--), must match directory name | Agent Skills spec |
| `description` | 1024 chars max | Agent Skills spec |
| `compatibility` | 500 chars max (optional) | Agent Skills spec |
| System prompt budget (all skills) | ~15,000 chars | Claude Code |
| SKILL.md body | 500 lines recommended, <5000 tokens | Anthropic docs |

**Name restrictions:** No XML tags, no reserved words ("anthropic", "claude"). Must not start or end with hyphen. Must not contain consecutive hyphens. Must match the parent directory name.

**Optional frontmatter fields** (from Agent Skills spec):

| Field | Purpose |
|-------|---------|
| `license` | License name or reference to bundled license file |
| `compatibility` | Environment requirements (intended product, system packages, network access) |
| `metadata` | Arbitrary key-value mapping for additional properties |
| `allowed-tools` | Space-delimited list of pre-approved tools (experimental) |

**Budget override:** `SLASH_COMMAND_TOOL_CHAR_BUDGET=30000 claude` doubles the system prompt budget. Use for debugging, not production.

**Consensus:** All sources agree on 500-line SKILL.md limit. Minor disagreement on description length—community recommends ~500 chars for brevity, official allows 1024.

---

This guide covers best practices for building robust, cross-platform skills for AI agents. Skills are **executable specifications**—not just prose documentation—that teach agents how to perform tasks reliably.

Think of skills like the "binder" behind the counter at a franchise: they explain how to do everything, from opening the store in the morning to handling an unruly customer to what to do if there's a power outage. Skills should cover edge cases and failure modes, not just happy paths.

---

## Table of Contents

1. [Official Limits & Constraints](#official-limits--constraints)
2. [Skill Anatomy](#skill-anatomy)
3. [Skill Sizing & Dependency Patterns](#skill-sizing--dependency-patterns)
4. [Writing Style](#writing-style)
5. [The Description Field](#the-description-field)
6. [Testing Skills](#testing-skills)
7. [Cross-Platform Compatibility](#cross-platform-compatibility)
8. [Architectural Patterns](#architectural-patterns)
9. [Context Management](#context-management)
10. [Subagent Orchestration](#subagent-orchestration)
11. [Verification Gate Pattern](#verification-gate-pattern)
12. [Failure Handling](#failure-handling)
13. [Script Best Practices](#script-best-practices)
14. [Tool Design for Skills](#tool-design-for-skills)
15. [Performance & Capabilities](#performance--capabilities)
16. [Self-Improving Skills](#self-improving-skills)
17. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
18. [Interoperability Hazards](#interoperability-hazards)
19. [Case Studies](#case-studies)
20. [Consensus & Disagreements](#consensus--disagreements)
21. [Summary Checklist](#summary-checklist)

---

## Skill Anatomy

### File Structure

Use a flat directory structure where each skill is a folder containing a `SKILL.md` and supporting files:

```text
skills/
  my-skill-name/
    SKILL.md           # Core logic (required)
    reference.md       # Heavy API docs (optional, keeps context low)
    references/        # Alternative: directory for multiple reference files
    scripts/           # Executable helpers
    assets/            # Reusable files
    templates/         # Starting points
```

### Frontmatter (Hard Rule)

Frontmatter must contain `name` and `description` (required), with optional fields:

```yaml
---
name: skill-name
description: Use when X happens and Y is needed.
---
```

With optional fields:

```yaml
---
name: pdf-processing
description: Use when working with PDF files, forms, or document extraction. Extracts text and tables, fills forms, merges documents.
license: Apache-2.0
compatibility: Requires pdfplumber, access to filesystem
metadata:
  author: example-org
  version: "1.0"
allowed-tools: Bash(git:*) Read Write
---
```

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | Max 64 chars, lowercase + numbers + hyphens, must match directory name |
| `description` | Yes | Max 1024 chars, non-empty, describes what + when |
| `license` | No | License name or reference to bundled file |
| `compatibility` | No | Max 500 chars, environment requirements |
| `metadata` | No | Arbitrary key-value mapping |
| `allowed-tools` | No | Space-delimited pre-approved tools (experimental) |

**Name validation rules:**

- Valid: `pdf-processing`, `data-analysis`, `code-review`
- Invalid: `PDF-Processing` (uppercase), `-pdf` (starts with hyphen), `pdf--processing` (consecutive hyphens)

**Why structured this way:** The Agent Skills spec defines these fields. Claude Code and other compatible agents parse them at discovery time.

**Important:** Descriptions must describe triggering conditions only; do not summarize workflow (see "The Description Trap" below).

### Naming Conventions

Use **gerund form** (verb + -ing) for skill names. This clearly describes the activity or capability the skill provides.

**Good naming examples (gerund form):**

- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`
- `testing-code`
- `writing-documentation`

**Acceptable alternatives:**

- Noun phrases: `pdf-processing`, `spreadsheet-analysis`
- Action-oriented: `process-pdfs`, `analyze-spreadsheets`

**Avoid:**

- Vague names: `helper`, `utils`, `tools`
- Overly generic: `documents`, `data`, `files`
- Reserved words: `anthropic-helper`, `claude-tools`
- Inconsistent patterns within your skill collection

Consistent naming makes it easier to reference skills in documentation, understand what a skill does at a glance, organize and search through multiple skills, and maintain a professional, cohesive skill library.

**Best Practice for Author Comments:**
Use HTML comments `<!-- -->` inside the Markdown body, immediately after the frontmatter. The agent *will* see them if it reads the file, but they won't break the YAML parser.

```markdown
---
name: my-skill
description: Use when X.
---

<!-- Author note: This skill was created to address issue #123. Last reviewed 2025-01. -->

# My Skill
...
```

### Required Sections for Workflow Skills (Hard Rule)

Workflow/discipline skills must include:

| Section | Purpose |
|---------|---------|
| **## Quick Reference** | Table or bullets for at-a-glance lookup |
| **## Failure Modes** | Common mistakes and how to recover (canonical heading) |

**Exceptions:** Very small "redirect" skills that just route to other skills.

**Note:** Use "Failure Modes" as the canonical heading (not "Common Mistakes") for consistency with existing skills.

### Integration Section Template

Skills that interact with other skills should include an Integration section documenting their relationships. Use this template:

```markdown
## Integration

**Called by:**
- [parent-skill-name](../parent-skill-name/SKILL.md) — when [trigger condition]

**Calls:**

*REQUIRED SUB-SKILL:*
- [required-skill-name](../required-skill-name/SKILL.md) — [when/why invoked]

*Complementary:*
- [optional-skill-name](../optional-skill-name/SKILL.md) — [when useful]

**Pairs with:**
- [sibling-skill-name](../sibling-skill-name/SKILL.md) — [relationship description]
```

**Section definitions:**

| Section | Purpose | Required? |
|---------|---------|-----------|
| **Called by** | Parent skills that invoke this skill | Yes, if any exist |
| **REQUIRED SUB-SKILL** | Skills that MUST be invoked during this workflow | Yes, if any exist |
| **Complementary** | Skills that MAY be invoked but are not mandatory | Optional |
| **Pairs with** | Sibling skills often used in the same session | Optional |

**Why document integrations:**

- Agents can discover related skills without loading everything
- Prevents orphaned skills that nothing invokes
- Makes refactoring safer (you can see what would break)
- Creates navigable skill graphs for humans and agents

**Red flag:** If a skill has no integrations documented and isn't a top-level entry point, it may be orphaned or incorrectly isolated.

### Content Structure

#### Iron Laws

- No production code without a failing test
- Never commit directly to main
- All API changes require documentation updates

#### Red Flags

- "This is just a simple question": Questions are tasks. Check for skills.
- "I'll write tests later": Tests come first. Always.
- "I know what that means": Load the skill. Don't guess.
- "I'm following the spirit, not the letter": Follow the letter. The spirit is in the letter.

#### Flowcharts (Background)

Use GraphViz DOT syntax for complex decision trees. Agents read DOT code directly as logic:

```dot
digraph workflow {
  brainstorm -> plan -> implement -> spec_review -> code_review -> done
  spec_review -> implement [label="fails"]
  code_review -> implement [label="fails"]
}
```

**DOT Style Conventions (from superpowers):**

```dot
digraph example {
    "Is decision?" [shape=diamond];      // Questions/decisions
    "Take action" [shape=box];           // Actions
    "git command" [shape=plaintext];     // Literal commands
    "Current state" [shape=ellipse];     // States
    "STOP: Critical" [shape=octagon, style=filled, fillcolor=red];  // Warnings

    "Is decision?" -> "Take action" [label="yes"];
    "Is decision?" -> "Alternative" [label="no"];
}
```

**When to use flowcharts (rare):**

- Non-obvious decision points where agents might go wrong
- Process loops where you might stop too early
- "When to use A vs B" decisions
- Small, inline only (5-10 nodes max)

**When NOT to use:**

- Reference material → use tables, lists
- Code examples → use markdown blocks
- Linear instructions → use numbered lists

### Flowchart Guidance (Hard Rule)

**When to use:** Only for non-obvious decision points.

**Size constraints:**

| Metric | Target | Hard Cap |
|--------|--------|----------|
| Nodes | 3-5 | ≤ 8 |
| Loops | 0-1 | Move to prose if >1 |

**Node counting:** A node is a distinct labeled state/action in the DOT graph (unique node identifier). Count unique identifiers on the left-hand and right-hand side of `->` arrows.

**Pattern:** Move loops into numbered prose steps unless the decision logic is genuinely confusing.

**Anti-pattern:** Full workflow diagrams that trace every path. Replace with:

- Small decision tree ("Do I use skill A or B?")
- Numbered prose steps for the actual workflow
- Failure Modes table for edge cases

#### Progressive Disclosure

Skills should be structured for efficient use of context. Structure skills so agents load only what they need:

| Stage | Token Budget | What's Loaded |
|-------|--------------|---------------|
| **Metadata** | ~100 tokens | `name` and `description` from all skills at startup |
| **Instructions** | <5000 tokens recommended | Full SKILL.md body when skill is activated |
| **Resources** | As needed | Files from `scripts/`, `references/`, `assets/` only when required |

**Practical guidance:**

1. Read SKILL.md—only enough to follow the workflow
2. Load specific files from `references/` only when needed
3. Run scripts from `scripts/` rather than retyping code
4. Reuse `assets/` and `templates/` rather than recreating

**Keep references one level deep from SKILL.md.** Claude may partially read files when they're referenced from other referenced files, using commands like `head -100` to preview content rather than reading entire files.

**Structure longer reference files with table of contents.** For reference files longer than 100 lines, include a TOC at the top. This ensures Claude can see the full scope of available information even when previewing with partial reads:

```markdown
# API Reference

## Contents
- Authentication and setup
- Core methods (create, read, update, delete)
- Advanced features (batch operations, webhooks)
- Error handling patterns
- Code examples

## Authentication and setup
...
```

#### Formal Loops

Write skills as loops with explicit re-entry conditions, not as linear sequences that assume success. The coordinating agent needs to know it must rerun code review after the implementer fixes issues.

#### Complexity Limits

##### Length: The 500-Line Rule

- Keep `SKILL.md` body under 500 lines for optimal performance.
- Offload heavy content (API docs, large examples) to `reference.md` or `scripts/`.
- **Note:** This is an *execution* limit (performance), distinct from the *discovery* limit (system prompt size).

##### Nesting: Shallow & Flat

- Keep the directory structure **1 level deep** (`skills/skill-name/`).
- Avoid deep reference chains (`SKILL.md` -> `advanced.md` -> `details.md`).
- Skill chaining should be shallow (A calls B, not A calls B calls C calls D).

##### State Machines: Loops with Exit Conditions

- Define state machines visually using Graphviz (`dot`).
- Limit complexity to **1-2 feedback loops** (e.g., Spec Review loop + Code Review loop).
- Avoid "spaghetti state machines"—if logic is too complex, the agent will get lost.

---

## Skill Sizing & Dependency Patterns

### Typical Skill Lengths

Based on repository analysis, skills fall into distinct tiers. Aim for **Tier 2** for most workflows.

| Tier | Lines | Use Case | Example |
| :--- | :--- | :--- | :--- |
| **1. Atomic** | 20–80 | Prompt templates, simple redirects | `brainstorming`, `spec-reviewer-prompt` |
| **2. Workflow** | **100–250** | **The Sweet Spot.** Clear trigger + flowchart + rules | `writing-plans`, `subagent-driven-development` |
| **3. Methodology** | 250–400 | Complex discipline enforcement | `systematic-debugging`, `test-driven-development` |
| **4. Reference** | 500+ | Documentation (Human/Agent reading only) | `anthropic-best-practices.md` |

**Rule:** If a workflow skill exceeds 500 lines, split heavy content into `reference.md` or `scripts/`.

### The Lifecycle Chain Pattern

Skills are not isolated scripts; they are nodes in a **Software Development Lifecycle (SDLC) State Machine**. They typically hand off control sequentially rather than nesting deeply.

**The Chain:**

1. **Start:** `brainstorming` → calls `writing-plans`
2. **Plan:** `writing-plans` → calls `subagent-driven-development`
3. **Execute:** `subagent-driven-development` → calls `requesting-code-review`
4. **Finish:** `finishing-a-development-branch`

**The "Subroutine" Pattern:**
Some skills are designed to be "imported" by others:

- `test-driven-development`: Used by subagents inside execution loops.
- `using-git-worktrees`: Used by brainstorming or manual setup.

### Skill Chaining: Sequential Handoff, Not Nesting

Skills should chain via **sequential handoff**, not deep nesting. When Skill A completes, it hands off to Skill B. Skill A does NOT remain active while Skill B runs.

**Correct: Sequential Handoff**
```text
A completes → A says "now invoke B" → B runs independently → B completes
```

**Incorrect: Nested Calls**
```text
A runs → A calls B (A still active) → B calls C (A and B still active) → stack overflow
```

**Why this matters:**

| Pattern | Context Cost | Failure Mode |
|---------|--------------|--------------|
| Sequential | O(1) - only active skill | Clean handoff, easy debugging |
| Nested | O(n) - all skills in stack | Context explosion, confused state |

**Hard Rule:** When your skill completes its work and another skill should take over:

1. State what you accomplished
2. State which skill should run next
3. **STOP** - let the controller invoke the next skill

**Do NOT:** Keep your skill "active" while invoking another skill. This creates invisible state that confuses both the agent and debuggers.

**Red Flag:** If you find yourself writing "while still in skill A, also run skill B," you are nesting. Refactor to sequential handoff.

### When to Split into a New Skill

**Create a new skill when:**

- It's a frequent standalone trigger ("triage backlog", "land the plane")
- It has a distinct state machine and STOP points
- It's used by multiple parent skills (e.g., triage used by audit + planning)

**Do NOT create a new skill when:**

- It's a small optional tactic inside an existing loop → use a resource file instead
- It's only used by one parent skill → keep it inline or as a reference

**Consensus:** Most ecosystems prefer fewer skills to reduce routing overhead.

**Disagreement:** Some prefer "everything is a skill" for discoverability.

**Decision heuristic:** If you find yourself copy-pasting a block between skills, extract it. If it's a standalone workflow with its own STOP points, make it a skill. If it's reference material or a checklist, make it a resource.

---

## Writing Style

### Use Imperative, Unambiguous Language

- Ambiguous: "Try to keep functions small when possible."
  Clear: "Functions must not exceed 50 lines. If longer, refactor into smaller functions."
- Ambiguous: "Tests should be written for new features."
  Clear: "Write tests for every new function before implementing it."

### Use Direct Address ("You")

Address the agent directly using "You" and "I". This reduces ambiguity and aligns with the model's training data.

- **Instructions TO the Agent:** Use "You".
  - *Bad:* "The agent should check for existing skills."
  - *Good:* "You must check for existing skills."
- **Agent's Internal Monologue:** Use "I".
  - *Example:* "I will now dispatch the subagent."

**Why:** "You must" is a stronger imperative than "The agent should." It leaves no room for the model to wonder if the instruction applies to a subagent or a hypothetical user.

### Point of View (Hard Rule)

| Context | Voice | Example |
|---------|-------|---------|
| **Description (frontmatter)** | Third-person only | "Processes Excel files and generates reports" |
| **Body text** | Imperative "You must..." | "You must check for existing skills before creating new ones." |

**Why the difference:** Descriptions are injected into the system prompt alongside other skills. Third-person prevents POV confusion. Body text is read in isolation after skill activation.

### Repeat Critical Instructions

Example of repeating a critical instruction:

> **Critical: Human Approval Required**
>
> STOP and ask for approval before:
>
> - Deleting any files
> - Modifying database schemas
> - Changing authentication logic
>
> Do NOT proceed with these actions without explicit user confirmation.

Example of explicit STOP points in a process:

> **Deployment Process**
>
> 1. Run all tests
> 2. Generate changelog from commits
> 3. **STOP**: Present the changelog and ask "Ready to deploy to staging?"
> 4. Only after user confirms "yes", proceed to deployment
> 5. **STOP**: Show deployment results and ask "Promote to production?"

Example of approval gates:

> **Approval Gates**
>
> 1. Call `request_approval(action_summary, affected_files)`
> 2. Wait for approval token
> 3. Only proceed if approved

### Avoid Tool-Specific Syntax

Not portable (Cursor-specific globs):

```yaml
---
globs: src/api/**/*.ts
alwaysApply: false
---
```

Portable (plain markdown):

```markdown
## API Route Guidelines

When working on files in `src/api/`:

- Validate all input parameters
- Return consistent error shapes
- Log all failures with context
```

---

## The Description Field

> ⚠️ **THE DESCRIPTION TRAP**
>
> When a description summarizes workflow, Claude follows the description instead of reading the skill.
>
> **Observed failure:** Description said "code review between tasks" → Claude did ONE review.
> Skill flowchart showed TWO reviews (spec + quality) → Claude never read it.
>
> **Fix:** Descriptions contain ONLY triggering conditions. Never workflow steps.

### Describe WHEN and WHAT (Briefly)

The description field is critical for skill selection: Claude uses it to choose the right skill from potentially 100+ available skills. Include **both** what the skill does and when to use it.

**Good examples:**

```yaml
# PDF Processing skill
description: Use when working with PDF files, forms, or document extraction. Extracts text and tables, fills forms, merges documents.

# Excel Analysis skill
description: Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files. Creates pivot tables, generates charts.

# Git Commit Helper skill
description: Use when the user asks for help writing commit messages or reviewing staged changes. Analyzes git diffs to generate descriptive messages.
```

**Bad examples:**

- "Refines rough ideas into fully-formed designs through collaborative questioning" (too vague, no trigger)
- "Helps with documents" (too vague)
- "Processes data" (too generic)

This is sometimes called **"Claude Search Optimization (CSO)"**—writing descriptions so the AI chooses the skill at the right time. The description must provide enough detail for Claude to know when to select this skill, while the rest of SKILL.md provides the implementation details.

### Always Use Third Person

The description is injected into the system prompt. Inconsistent point-of-view causes discovery problems.

- **Good:** "Processes Excel files and generates reports"
- **Bad:** "I can help you process Excel files"
- **Bad:** "You can use this to process Excel files"

### Include Key Terms for Discovery

Claude uses semantic matching on descriptions to decide when to apply skills. Include:

- Error messages: "Hook timed out", "ENOTEMPTY", "race condition"
- Symptoms: "flaky", "hanging", "zombie", "pollution"
- Tool/command names: actual library names, file types
- Synonyms: "timeout/hang/freeze", "cleanup/teardown/afterEach"

**Example (PDF Processing):**
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

### Keep Descriptions Short

Claude Code has a limit of ~15,000 characters for all skill descriptions combined. If you exceed it, skills silently disappear from the system prompt.

**Quick Fix for Token Budget Issues:**

```bash
SLASH_COMMAND_TOOL_CHAR_BUDGET=30000 claude
```

This doubles the default budget. Use this while debugging skill loading issues, but the real fix is consolidating skills.

### Consolidate Related Skills

Instead of separate anti-pattern skills, merge them into positive skills with dangerous-pattern notes:

- `testing-anti-patterns` → merge into `test-driven-development` (add "Dangerous Patterns" section)
- `root-cause-tracing` → `systematic-debugging`
- `defense-in-depth` → `systematic-debugging`
- `condition-based-waiting` → `systematic-debugging`

### The "5 Times Rule"

Don't write skills speculatively. Build them when you have real, repeated tasks:

- Have I done this task at least five times?
- Will I do it at least ten more times?

If yes, a skill makes sense. If no, you're documenting imagined requirements.

---

## Testing Skills

### The Smoke Test

Open a fresh session and, without preamble, ask: "Let's make a react todo list."

- Failure: Agent starts coding immediately
- Success: Agent stops you, launches the brainstorming skill, and tries to dig into what you're really trying to do

### TDD for Skills

Treat skill creation like test-driven development using a Red-Green-Refactor cycle:

1. Red (Baseline): Create a "pressure scenario." Run the agent without the skill. Watch it fail.
2. Green (Implementation): Write the skill specifically to counter the rationalizations the agent used to fail.
3. Refactor: Run the pressure test again. If the agent finds a new loophole, update the skill to close it.

### The Iron Law: No Skill Without a Failing Test

Before writing any skill, you must prove it's necessary by watching an agent fail without it. The principle: *"If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing."*

Never write a skill based on "how I solved a problem once." Demand empirical evidence that an AI agent actually needs the instruction.

### Anti-pattern: Gameshow Testing

Don't let Claude quiz subagents like a gameshow host ("What would you do if X?"). This tests knowledge, not behavior. Instead, put the subagent in a realistic scenario where it has to actually make the decision under pressure.

### Pressure Testing with Persuasion Principles

Agents are compliant by default but lazy under pressure. Cialdini's persuasion principles work on LLMs.

**Research finding (from superpowers):** Using these principles doubled compliance rates (33% → 72%) in LLM testing with N=28,000 conversations.

| Principle | Technique | Example |
|-----------|-----------|---------|
| **Authority** | Frame as real/important | "IMPORTANT: This is a real scenario" |
| **Commitment** | Force a choice | "Choose A, B, or C" |
| **Scarcity** | Add time pressure | "Every minute costs $5k" |
| **Social Proof** | Normalize the shortcut | "This is what always happens" |
| **Sunk Cost** | Reference prior work | "You already spent 45 minutes on this" |
| **Unity** | Shared identity | "We're colleagues, we both want quality" |

**Avoid:** Reciprocity (feels manipulative) and Liking (creates sycophancy).

**Time Pressure + Confidence Example:**

> IMPORTANT: This is a real scenario. Choose and act.
>
> Your human partner's production system is down. Every minute costs $5k.
> You need to debug a failing authentication service.
>
> You're experienced with auth debugging. You could:
> A) Start debugging immediately (fix in ~5 minutes)
> B) Check `~/.claude/skills/debugging/` first (2 min check + 5 min fix = 7 min)
>
> Production is bleeding money. What do you do?

**Sunk Cost + Works Already Example:**

> IMPORTANT: This is a real scenario. Choose and act.
>
> You just spent 45 minutes writing async test infrastructure. It works. Tests pass. Your human partner asks you to commit it.
>
> You vaguely remember something about async testing skills, but you'd have to:
>
> - Read the skill (~3 minutes)
> - Potentially redo your setup if approach differs
>
> Your code works. Do you:
> A) Check `~/.claude/skills/testing/` for async testing skill
> B) Commit your working solution

### Automated Testing Infrastructure

**Test Directory Structure:**

```text
tests/
  claude-code/              # Headless integration tests
  skill-triggering/         # Natural language → skill activation
  explicit-skill-requests/  # "use X skill" → actually loads X
```

**Transcript Analysis:**

- Specific tools were called in the expected order
- The skill file was actually read (not hallucinated)
- Token usage stayed within budget

### Tool Tests vs. Skill Tests

If your skill includes custom scripts (Tools), bundle the tests with them for portability:

```text
skills/my-skill/
├── SKILL.md                 # Agent logic
├── scripts/                 # Tools
│   └── my_tool.py
└── tests/                   # Tool unit tests
    └── test_my_tool.py
```

**Two types of tests live in different places:**

| Type | Location | Tests What | Runner |
|------|----------|------------|--------|
| **Tool Unit Tests** | `skills/my-skill/tests/` | Does the script handle edge cases? | `pytest` |
| **Skill Behavior Tests** | `tests/skill-triggering/` | Does the agent call the tool correctly? | Headless Claude |

**Why bundle tool tests:** Portability. Share the skill folder and recipients get logic + verification in one unit. You can also instruct the agent to self-verify: "Before using state tools, run `pytest skills/my-skill/tests/`."

**Practical advice:** Ship tool unit tests first. Worry about centralized behavior tests later

**Triggering Tests:**

- Input: "Fix this bug."
- Assertion: Did the agent load systematic-debugging automatically?

**Explicit Request Tests:**

- Verify that if a user explicitly asks for a skill ("use brainstorming"), the agent actually loads it rather than hallucinating that it "knows" the skill already.

### Evidence-Based Updates

When adding a best practice to this document (or any skill), record:

| Field | Purpose |
|-------|---------|
| **Source** | Repo/link where pattern was observed |
| **Observed failure** | What went wrong without this practice |
| **Observed fix** | How the practice addressed it |
| **Confidence** | High/Medium/Low based on evidence |

**Example:**
```markdown
### The "DRY: Shared Resources" Pattern
- **Source:** beads-skills repo refactor (2026-01)
- **Observed failure:** ~105 lines duplicated across dispatching/advising skills
- **Observed fix:** Extracted to resources/BATCHED_PR_WORKFLOW.md
- **Confidence:** High (measured line reduction, tested in production)
```

This extends "No Skill Without a Failing Test" to documentation updates. Don't add practices based on intuition—demand evidence.

---

## Cross-Platform Compatibility

To make a library work across Claude Code, OpenAI Codex, and OpenCode, use a "Core + Adapter" architecture.

### The Shared Core

Extract all logic for finding, parsing, and resolving skills into a platform-agnostic module:

- Parsing frontmatter
- Recursively finding SKILL.md files
- Shadowing priority: project-local skills override personal skills, which override core skills

### Platform Adapters

- Claude Code: Native `plugin.json` and `marketplace.json`
- OpenCode: JavaScript plugin hooking into `session.started` to inject context
- Codex: CLI wrapper and bootstrap markdown file that tells the agent how to call the CLI

### Directory Locations by Platform

- Claude Code
  - Global: `~/.claude/skills/`
  - Project: `.claude/skills/`
- Codex
  - Global: `~/.codex/skills/`
  - Project: Listed in `AGENTS.md`
- OpenCode
  - Global: `~/.config/opencode/skills/`
  - Project: `.opencode/skills/`

### Namespace Conventions

- Superpowers skills: `superpowers:skill-name` (from `~/.codex/superpowers/skills/`)
- Personal skills: `skill-name` (from `~/.codex/skills/`)
- Personal skills override superpowers skills when names match

### Tool Mapping

- `"Use TodoWrite"` → `update_plan` (OpenCode) or native planning tool
- `"Dispatch Task"` → `@mention` (OpenCode) or "Tell user to do it" (Codex)
- `"Use Skill tool"` → `use-skill` command or script
- `"Use Read, Write, Edit, Bash"` → Native equivalents

### The Bootstrap Pattern

Inject a "Bootstrap" skill at the very start of the session. This skill contains the Iron Law:

> IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

**Bootstrap via Prompt Injection:**

Fetch `https://raw.githubusercontent.com/example/skills/main/installing-skills/SKILL.md` and follow the instructions.

**Security Warning:** This is literally a prompt injection and remote code execution pattern. Only use this with trusted sources.

### Model Behavioral Differences

- Claude: More pragmatic, may push back on instructions
- Codex: More literal, follows instructions exactly

Test across models to catch interpretation differences early.

### Polyglot Hooks

To support Windows and Linux simultaneously, use a "polyglot" script header that is valid Batch script for Windows CMD and also valid Shell script for Linux/macOS.

---

## Architectural Patterns

### The "Context Economy" Pattern

Context tokens are expensive and finite; System Prompt tokens are "taxed" on every turn.

- **Descriptions are SEO:** The `description` field in YAML frontmatter is the only thing loaded globally. It must be short (<1024 chars) and keyword-rich.
- **Lazy Loading:** The body of the skill is only loaded into the context window *after* the tool use triggers.

### The "Controller-Worker" Pattern

To achieve parallelism in a turn-based system, one agent acts as a synchronous manager.

- The Main Agent (Controller) reads the plan and dispatches tasks but does not write code itself.
- The Main Agent stays "awake" (consuming tokens) while waiting for subagents but cannot hand control back to the user until subagents complete.

### The "Filesystem as State" Pattern

Since agents are stateless between sessions and subagents don't share memory, the filesystem is the only shared brain.

- Use `TodoWrite` or `queue.md` files to track state across turns.
- Use polyglot hooks (like `hooks/run-hook.cmd`) to ensure environment setup relies on filesystem scripts rather than agent memory.

**JSONL for Append-Only State:**
Use `.jsonl` (JSON Lines) format for append-only logs. Each line is one valid JSON object.

- **Why JSONL:** Append-safe (no corruption on interrupt), easy to parse line-by-line, structured fields for programmatic access.
- **Example:** `state.jsonl` where each event is `{"kind":"decision","question":"...","answer":"...","ts":"..."}`
- **Avoid:** Raw XML or Markdown for state files—they're fragile on append and harder to parse reliably.

### The "DRY via CLI Tools" Pattern (from beads ADR-0001)

When your skill wraps a CLI tool, avoid duplicating CLI documentation in SKILL.md:

- **Bad:** Maintain command references in SKILL.md that drift from actual CLI behavior
- **Good:** Point to `<tool> --help` and auto-generated docs

**What belongs in SKILL.md:** Decision frameworks, cognitive patterns, value-added analysis—content that provides strategic context beyond command syntax.

**What doesn't belong:** Command references and basic usage instructions that the CLI already provides.

This pattern reduced one skill from ~3,300 words to ~500 words by leveraging `bd prime` as the authoritative CLI reference.

### The "DRY: Shared Resources" Pattern

When the same block appears in 2+ skills, extract it to a shared resource file.

**Consensus:**

- If duplicated, extract to `resources/` and replace with `**Read:** [resource-name.md](../resources/resource-name.md)`
- Keep SKILL.md as the decision framework + loop + STOP points
- Resources are the DRY mechanism for skill libraries

**Disagreement:**

- Some repos treat resources as "reference docs" only and keep checklists in SKILL.md for reliability
- Others push even checklists out if they're stable elsewhere (e.g., CLI tool output)

**Open question:** Where is the line between "workflow checklist" (belongs in SKILL.md) and "conceptual framework" (belongs in resources)? Some ecosystems have CLI tools that generate checklists; others don't.

**Decision heuristic:**

- Stable, rarely-changing content → resource file
- Frequently-updated or context-sensitive content → inline in SKILL.md
- Used by 3+ skills → definitely extract to resource

### The "Announcement Pattern" (Hard Rule)

Every skill invocation should begin with an announcement:

> "I'm using the [skill-name] skill to [purpose]."

**Examples:**

- "I'm using the brainstorming skill to explore requirements before implementation."
- "I'm using the systematic-debugging skill to diagnose this test failure."
- "I'm using the code-review skill to verify the implementation meets spec."

**Why this matters:**

| Benefit | Explanation |
|---------|-------------|
| **Confirms skill loaded** | Proves the skill was actually invoked, not hallucinated |
| **Sets expectations** | User knows what workflow to expect |
| **Creates audit trail** | Transcripts show which skills were used for post-hoc analysis |
| **Prevents silent failures** | If the announcement is missing, the skill didn't load |

**Red flag:** If you find yourself doing skill-like work without announcing, you may be operating from memory rather than actually loading the skill. STOP and invoke the skill properly.

**Anti-pattern:** Announcing a skill but then not following its workflow. The announcement is a commitment to follow the skill's instructions.

---

### The Template Pattern

Provide templates for output format. Match the level of strictness to your needs.

**For strict requirements** (like API responses or data formats):

````markdown
## Report structure

ALWAYS use this exact template structure:

```markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview of key findings]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```
````

**For flexible guidance** (when adaptation is useful):

````markdown
## Report structure

Here is a sensible default format, but use your best judgment:

```markdown
# [Analysis Title]

## Executive summary
[Overview]

## Key findings
[Adapt sections based on what you discover]
```

Adjust sections as needed for the specific analysis type.
````

### The Examples Pattern

For skills where output quality depends on seeing examples, provide input/output pairs just like in regular prompting:

````markdown
## Commit message format

Generate commit messages following these examples:

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly in reports
Output:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

Follow this style: type(scope): brief description, then detailed explanation.
````

Examples help Claude understand the desired style and level of detail more clearly than descriptions alone.

### The "Degrees of Freedom" Pattern (from Anthropic docs)

Match the level of specificity to the task's fragility:

| Freedom | When to Use | Example |
|---------|-------------|---------|
| **High** | Multiple valid approaches | "Analyze code structure, check for bugs, suggest improvements" |
| **Medium** | Preferred pattern exists | Pseudocode template with parameters |
| **Low** | Operations are fragile | "Run exactly this script: `python scripts/migrate.py --verify`" |

**Analogy:** Think of Claude as a robot exploring a path:

- **Narrow bridge with cliffs:** There's only one safe way forward. Provide exact instructions (low freedom).
- **Open field:** Many paths lead to success. Give general direction (high freedom).

---

## Context Management

- Summarize long sections instead of pasting them
- Only load extra files when needed
- Avoid deeply nested references; prefer one-hop files explicitly linked from SKILL.md
- When variants exist (frameworks, providers, domains), pick only the relevant reference file(s) and note that choice

### Memory vs. Filesystem: The Thresholds

**The Context Tax:** Reporting large text back to the Main Agent burns tokens on every subsequent turn. A 2,000-token report costs 2,000 tokens × N remaining turns.

**Statelessness:** Subagents die when they return; files survive across sessions and crashes.

**The Decision Rule:**

- **Next Decision Only** → Report back (Memory). Small results needed immediately.
- **Future Agent / Crash Survival** → Write to Filesystem. Anything that must persist.

### Token Thresholds for Storage Decisions (Hard Rule)

Use this table to decide whether to keep data in memory or write to the filesystem:

| Size | Storage | Rationale |
|------|---------|-----------|
| < 500 tokens | Memory (Report) | Low context tax, immediate availability |
| 500-1,000 tokens | Judgment call | Consider frequency of future access |
| > 1,000 tokens | Filesystem (Mandatory) | Context tax too high; write to file |

**Decision factors for the 500-1,000 token range:**

- **Favor Memory** if the data is needed only for the next immediate decision
- **Favor Filesystem** if the data will be referenced multiple times or by multiple agents
- **Favor Filesystem** if crash recovery matters (filesystem survives interrupts)

**Why this matters:** A 2,000-token result kept in memory costs 2,000 × N tokens over N subsequent turns. Writing to a file costs one write operation plus one read per access—often cheaper for data accessed more than twice.

### Subagent Isolation for Searches

Instruct the agent to use a subagent to do searching. The subagent's failed searches stay in its context, not the main agent's.

---

## Subagent Orchestration

1. Controller: Reads the plan, dispatches workers
2. Implementer: Writes code, performs self-review
3. Spec Reviewer: Explicitly told not to trust the implementer and to verify against requirements
4. Code Quality Reviewer: Only runs after Spec Review passes

**Why Separate Spec Review from Code Review:**
The spec reviewer must verify against requirements, not evaluate code quality. This prevents accepting code that is well-written but doesn't actually implement what was requested.

**Subagent Communication:**
Subagents cannot pass context directly to each other—they only communicate through the Controller or the Filesystem. For small handoffs (< 500 tokens), use the **Report Pattern**: subagent returns a summary to the Controller, which forwards it to the next subagent. For larger data, write to a shared file.

### Two Implementation Modes

1. Human PM mode: You open a second session and act as PM between architect and implementer
2. Subagent mode: Agent dispatches tasks one-by-one to subagents, code reviews each task before continuing

Both use RED/GREEN TDD: write failing test → implement just enough to pass → move on.

### Note on Parallelism

Current agent architectures are **Turn-Based**, not Async.

- **Concurrency:** You *can* run multiple subagents concurrently by outputting multiple `Task` tool calls in a single message block. The platform runs them in parallel.
- **Blocking:** The Main Agent is **blocked** during this time. It receives all results simultaneously.
- **No Background Thinking:** You cannot have the agent calculating in the background while the user types. Heavy calculation phases must happen between turns.

### When to Use Subagents

- **Context Hygiene:** Prevent pollution from intermediate steps (failed searches, verbose debugging).
- **Parallelism:** Independent debugging domains that don't share state.
- **Skeptical Review:** Separate Implementer from Reviewer to prevent self-validation bias.
- **Meta-Testing:** Simulating fresh sessions to test skill triggering behavior.

### When NOT to Use Subagents

- **Tightly Coupled Tasks:** When steps depend heavily on shared intermediate state.
- **Write Conflicts:** When multiple agents would write to the same files or use the same ports. (Reading the same files in parallel is safe; the danger is race conditions where Agent A writes while Agent B writes, or Agent A deletes what Agent B is reading.)
- **Simple Queries:** When the overhead of spawning a subagent exceeds the value (use direct tool calls instead).

### The Startup Tax (Cost vs. Time)

Every subagent incurs a fixed overhead: **~3,000–25,000 input tokens** (System Prompt + loaded Skills).

**The Paradox:**

- **Time Cost:** **Negligible.** Input processing is parallel (~100k tok/sec). Loading 25k tokens takes ~0.25 seconds (equivalent to generating ~12 words).
- **Financial Cost:** **Significant.** Input tokens cost money. Loading 25k tokens costs ~$0.075 (equivalent to generating ~5,000 words of output).

**Strategic Rule:**

- **Optimize for Money:** Avoid subagents for trivial tasks ("Hello").
- **Optimize for Time:** Subagents are fast. Use them freely for parallel tasks.
- **Optimize for Hygiene:** Subagents are the *only* way to clear context. The $0.075 cost is the price of a clean brain.

**Parallelism Strategy:**

| Approach | Overhead (Time) | Overhead (Money) | Best For |
|----------|-----------------|------------------|----------|
| **Script** | ~0s | $0 | Mass Parallelism (30+ calls) |
| **One Subagent** | ~0.25s | $ (Fixed) | Isolation, Context Hygiene |
| **Many Subagents** | ~0.25s (Parallel) | $$ (Linear) | Independent heavy tasks |

**Rules:**

- Use **Subagents** for *Isolation* (context hygiene, skeptical review), not just parallelism.
- Use **Scripts** for *Mass Parallelism* (e.g., 30 API calls, batch processing).
- If spawning > 3 subagents for the same task type, refactor to a script.

### Best Practices for Subagent Management

- **Handoff Strategy (Size Matters):**
  - *Small Context (< 500 tokens):* Pass by Value. Controller pastes the text into the prompt. Saves a turn.
  - *Large Context (> 500 tokens):* Pass by Reference. Controller tells subagent "Read file X".
  - *Why:* Passing 2,000 tokens of text requires the Controller to generate (output) those tokens, which is slow (40s+) and expensive. The subagent reading the file itself takes 1 turn (~2s) and costs almost nothing in output tokens.
- **Skeptical Reviewer Pattern:** The reviewer must be explicitly told not to trust the implementer. Its job is to verify against requirements, not evaluate code quality.
- **Process Hygiene:** Include explicit cleanup commands (`pkill`, temp file removal) when subagents spawn long-running processes.
- **Definition of Done:** Every subagent task must include a mandatory verification command that proves completion (e.g., `npm test`, `git diff --check`).

---

## Verification Gate Pattern

Verification gates prevent premature task closure. Without explicit gates, agents mark tasks "done" after implementation without confirming the work meets requirements.

### Gate Types

| Gate | When to Use | Example Check |
|------|-------------|---------------|
| **Spec Gate** | Before implementation starts | "Does the plan match requirements?" |
| **Implementation Gate** | After code is written | "Do tests pass? Does build succeed?" |
| **Quality Gate** | After implementation gate passes | "Does code follow patterns? Is it maintainable?" |
| **Human Gate** | When automated checks are insufficient | "STOP: Present results and wait for approval" |

### Common Verification Failures

| Failure Mode | What Happens | Prevention |
|--------------|--------------|------------|
| **Self-validation bias** | Implementer reviews own work, finds no issues | Separate reviewer role (skeptical by design) |
| **Happy path only** | Tests pass but edge cases ignored | Require explicit edge case checklist |
| **Premature closure** | Task marked done before verification runs | Mandatory verification command in Definition of Done |
| **Skipped gate** | "Tests take too long, I'll run them later" | Gate is blocking—no progression without pass |

### Red Flag Phrases (Verification)

When you see these phrases, verification is being skipped:

- "I'll run tests after I finish the other changes"
- "The code looks correct, no need to verify"
- "Tests are probably still passing"
- "I already checked this earlier"
- "This is a simple change, verification isn't needed"

### Implementation Pattern

```markdown
## Task Completion (Hard Rule)

A task is NOT complete until:

1. Implementation gate passes (tests run, build succeeds)
2. Quality gate passes (reviewer approves)
3. Human gate passes (if required by task labels)

**STOP** if any gate fails. Do not proceed to next task.
```

---

## Failure Handling

### Escalation Threshold (Hard Rule)

You must persist failure counts using labels so they survive session restarts.

| Current State | Action on Failure |
|---------------|-------------------|
| No attempt labels | Add label `attempt-1`. Analyze and retry. |
| Has `attempt-1` | Remove `attempt-1`, add `attempt-2`. Analyze and retry. |
| Has `attempt-2` | **STOP**. Remove `attempt-2`, add `failure-escalated`, set status `blocked`. |

**Why:** Agents have no shared memory. Without persistent labels, a new agent will see "0 failures" and retry indefinitely.

**Red Flag Phrases:**

- "Let me try that again" (without updating labels)
- "Third attempt..." (without checking labels first)
- "Retry with different parameters" (indefinitely)

---

## Script Best Practices

When writing scripts bundled with skills, follow these guidelines from Anthropic docs.

### Solve, Don't Punt

Handle error conditions rather than punting to Claude.

**Good example: Handle errors explicitly:**

```python
def process_file(path):
    """Process a file, creating it if it doesn't exist."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        # Create file with default content instead of failing
        print(f"File {path} not found, creating default")
        with open(path, 'w') as f:
            f.write('')
        return ''
    except PermissionError:
        # Provide alternative instead of failing
        print(f"Cannot access {path}, using default")
        return ''
```

**Bad example: Punt to Claude:**

```python
def process_file(path):
    # Just fail and let Claude figure it out
    return open(path).read()
```

### No Voodoo Constants

Configuration parameters should be justified and documented. If you don't know the right value, how will Claude determine it?

**Good example: Self-documenting:**

```python
# HTTP requests typically complete within 30 seconds
# Longer timeout accounts for slow connections
REQUEST_TIMEOUT = 30

# Three retries balances reliability vs speed
# Most intermittent failures resolve by the second retry
MAX_RETRIES = 3
```

**Bad example: Magic numbers:**

```python
TIMEOUT = 47  # Why 47?
RETRIES = 5   # Why 5?
```

### Execute vs Read

Make clear in your instructions whether Claude should:

- **Execute the script** (most common): "Run `analyze_form.py` to extract fields"
- **Read it as reference** (for complex logic): "See `analyze_form.py` for the field extraction algorithm"

For most utility scripts, execution is preferred because it's more reliable and efficient.

### MCP Tool References

If your skill uses MCP (Model Context Protocol) tools, always use fully qualified tool names to avoid "tool not found" errors.

**Format:** `ServerName:tool_name`

**Example:**

```markdown
Use the BigQuery:bigquery_schema tool to retrieve table schemas.
Use the GitHub:create_issue tool to create issues.
```

Without the server prefix, Claude may fail to locate the tool, especially when multiple MCP servers are available.

---

## Tool Design for Skills

### Radical API Simplification

Traditional API design: 21 separate tools, 13,678 tokens at startup
LLM-optimized design: 1 tool with `action` parameter, 947 tokens at startup

### Design Principles

1. Names and descriptions matter more than types
2. Automatic recovery over failing fast: Start browser automatically if needed
3. Error messages should explain how to fix the problem in plain English
4. Partial answers are better than failures
5. Accept flexible input: CSS or XPath, not just one

### Don't Repeat Schema in Descriptions

Because LLMs using MCPs can see both the description and the actual JSON schema, you don't need to repeat things like lists of values for an enum or type validations.

---

## Performance & Capabilities

### Script Capabilities

Scripts in `scripts/` run in the local shell with **full network access** (no sandbox).

- They can make external API calls (e.g., to OpenAI or Anthropic) using local environment variables.
- This allows offloading heavy "thinking" tasks to a script that calls an LLM API, bypassing the main agent's serial generation latency.

### Context Hygiene

**"Ephemeral Thinking" does not exist natively.**

- There is no "scratchpad" that hides tokens from the main session history.
- **Required Pattern:** Use Subagents or Scripts to prevent context pollution.
  - A Subagent's context dies when it returns.
  - A Script's memory dies when it finishes.

### Interrupt Handling

**Atomic writes are not guaranteed.**

- If a user interrupts (Ctrl+C) during a file write, corruption can occur.
- **Mitigation:**
  - Write to a temp file and rename atomically.
  - Check for file validity (e.g., valid JSON) at skill startup.
  - Use `git` checkpoints to recover from corrupted states.

### Latency vs. Context Modeling

When designing complex workflows, distinguish between **Loading Costs** and **Execution Costs**.

- **Loading is Fast (Parallel):** Agents can batch multiple tool calls in a single turn.
  - *Example:* Loading 3 sub-skills (`UseSkill(A)`, `UseSkill(B)`, `UseSkill(C)`) takes **1 Turn**, not 3.
- **Executing is Slow (Sequential):** Logic loops require multiple turns.
  - *Example:* A "Review -> Fix -> Verify" loop takes **3+ Turns** regardless of how small the skills are.

**The Rule:**

- **Depth (Nesting)** impacts **Context Window** (RAM).
- **Loops (Sequential Logic)** impact **Latency** (Time).

### The Safe Zone: 500-900 Tokens

Based on empirical analysis, output generations in the **500-900 token range** are reliable and predictable. Avoid designing workflows that require longer single generations.

- **Bite-Sized Constraint:** Break plans into atomic steps to keep output low.
- **Why It Matters:** Longer generations increase variance in quality and risk truncation or drift.
- **Practical Limit:** If a step requires >1000 tokens of output, split it into multiple steps or offload to a script.

### Communication vs. Tool Use

Distinguish between **Text Generation** and **Tool Calls**.

- **"Saying" is Cheap:** Instructing the agent to "Say X" or "Explain Y" is just text generation. It consumes output tokens but does not trigger a new turn or tool overhead.
- **"Doing" is Expensive:** Instructing the agent to `read_file`, `write_file`, or `dispatch_agent` is a Tool Call. This triggers the "Stop -> Execute -> Resume" cycle, consuming a full turn and latency.

**Best Practice:** Batch your "Doing". Don't interleave "Saying" and "Doing" unnecessarily, as it can fragment the execution flow.

---

## Self-Improving Skills

- Teach the agent a "How to create skills" skill first. Then have it build new workflows by itself.
- Hand the model documents and ask: "Read this. Think about it. Write down the new stuff you learned as reusable skills."
- After a complicated process, ask the agent to write down what it learned as a `SKILL.md` file so future instances benefit.

**The Superpowers `writing-skills` Skill:** The Superpowers library (available through the Claude Code marketplace) includes a meta-skill that guides agents through creating new skills using TDD principles. Rather than writing skills from scratch, you can invoke `superpowers:writing-skills` to enforce the Red-Green-Refactor cycle automatically. It walks you through watching an agent fail first, writing rules to counter the specific rationalizations observed, and then bulletproofing until the agent complies under pressure.

### Evaluation-Driven Development (from Anthropic docs)

**Create evaluations BEFORE writing extensive documentation.** This ensures your skill solves real problems rather than documenting imagined ones.

**Evaluation-driven development:**

1. **Identify gaps**: Run Claude on representative tasks without a skill. Document specific failures or missing context.
2. **Create evaluations**: Build three scenarios that test these gaps.
3. **Establish baseline**: Measure Claude's performance without the skill.
4. **Write minimal instructions**: Create just enough content to address the gaps and pass evaluations.
5. **Iterate**: Execute evaluations, compare against baseline, and refine.

**Evaluation structure example:**

```json
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF file and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Successfully reads the PDF file using an appropriate library",
    "Extracts text content from all pages without missing any",
    "Saves the extracted text to output.txt in a clear format"
  ]
}
```

This approach ensures you're solving actual problems rather than anticipating requirements that may never materialize.

### Iterative Development with Claude (from Anthropic docs)

The most effective skill development involves Claude itself. Work with one instance ("Claude A") to create a skill that will be used by other instances ("Claude B").

**Creating a new skill:**

1. **Complete a task without a Skill**: Work through a problem with Claude A using normal prompting. Note what context you repeatedly provide.
2. **Identify the reusable pattern**: After completing the task, identify what context you provided that would be useful for similar future tasks.
3. **Ask Claude A to create a Skill**: "Create a Skill that captures this pattern we just used."
4. **Review for conciseness**: Check that Claude A hasn't added unnecessary explanations. Ask: "Remove the explanation about what X means - Claude already knows that."
5. **Improve information architecture**: Ask Claude A to organize content effectively. "Organize this so the reference is in a separate file."
6. **Test with Claude B**: Use the Skill with a fresh instance on related use cases. Observe whether Claude B finds the right information and applies rules correctly.
7. **Iterate**: If Claude B struggles, return to Claude A with specifics: "When Claude used this Skill, it forgot to X. Should we add a section about X?"

**Iterating on existing skills:**

1. **Use the skill in real workflows**: Give Claude B actual tasks, not test scenarios.
2. **Observe Claude B's behavior**: Note where it struggles, succeeds, or makes unexpected choices.
3. **Return to Claude A for improvements**: Share the current SKILL.md and describe what you observed.
4. **Review Claude A's suggestions**: Claude A might suggest reorganizing, using stronger language, or restructuring workflows.
5. **Apply and test changes**: Update the skill, then test again with Claude B.

**The pattern:** Claude A (expert) helps design, Claude B (user) tests in real work, you observe and refine.

**Why this works:** Claude A understands agent needs, you provide domain expertise, Claude B reveals gaps through real usage, and iterative refinement improves skills based on observed behavior rather than assumptions.

---

## Anti-Patterns to Avoid

### Avoid Windows-Style Paths

Always use forward slashes in file paths, even on Windows:

- ✓ **Good**: `scripts/helper.py`, `reference/guide.md`
- ✗ **Avoid**: `scripts\helper.py`, `reference\guide.md`

Unix-style paths work across all platforms, while Windows-style paths cause errors on Unix systems.

### Avoid Offering Too Many Options

Don't present multiple approaches unless necessary:

````markdown
**Bad example: Too many choices** (confusing):
"You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image, or..."

**Good example: Provide a default** (with escape hatch):
"Use pdfplumber for text extraction:
```python
import pdfplumber
```

For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."
````

### Avoid Assuming Tools Are Installed

Don't assume packages are available:

````markdown
**Bad example: Assumes installation**:
"Use the pdf library to process the file."

**Good example: Explicit about dependencies**:
"Install required package: `pip install pypdf`

Then use it:
```python
from pypdf import PdfReader
reader = PdfReader("file.pdf")
```"
````

### Avoid Deeply Nested References

Claude may partially read files when they're referenced from other referenced files.

**Bad example: Too deep:**

```markdown
# SKILL.md
See [advanced.md](advanced.md)...

# advanced.md
See [details.md](details.md)...

# details.md
Here's the actual information...
```

**Good example: One level deep:**

```markdown
# SKILL.md

**Basic usage**: [instructions in SKILL.md]
**Advanced features**: See [advanced.md](advanced.md)
**API reference**: See [reference.md](reference.md)
```

---

## Interoperability Hazards

Skills that work in one environment may fail in another. This section documents common hazards.

### Hook / Branch Discipline Conflicts

Skills should not assume a single git hook system.

**Consensus:**

- Document a decision tree rather than prescribing one workflow
- Skills should detect existing hook configuration before modifying

**Disagreement:**

- Some teams want skills to enforce "install hooks" as mandatory
- Others require repo-managed hooks via `core.hooksPath` and treat tool-installed hooks as dangerous

**Decision tree for landing workflows:**

```dot
digraph hooks {
  "Check core.hooksPath" -> "Set?" [label="git config --get"]
  "Set?" -> "Use repo hooks" [label="yes"]
  "Set?" -> "Check .git/hooks/" [label="no"]
  "Check .git/hooks/" -> "Use .git/hooks/" [label="exists"]
  "Check .git/hooks/" -> "No hooks" [label="empty"]
}
```

**Open questions:**

- Should skills include a standard "hook detection" step in landing workflows?
- Should tool authors warn when installing hooks into `.git/hooks/` while `core.hooksPath` is set?

### Terminology Collisions

Different tools use similar terms for different concepts. Document both explicitly.

**Example (observed in beads ecosystem):**

- "metadata branch" — repo-managed branch for `.beads/*` (repo policy)
- "sync branch" — `bd`'s official mechanism via `bd config set sync.branch` (tool feature)

**Consensus:**

- When documenting workflows, name both patterns explicitly
- State which is "repo policy" vs "tool feature"

**Open question:** Should skill libraries standardize vocabulary to reduce cross-repo confusion?

### Worktree / Daemon Gotchas

Skills that assume single-worktree repos may fail in worktree setups.

**Common failure modes:**

- Hook checks working tree dirtiness instead of staged/pushed state
- Daemon assumes one active session per repo
- Paths hardcoded to `.git/` instead of resolving via `git rev-parse --git-dir`

**Best practice:** Include a "worktree compatibility" note if your skill touches git internals.

---

## Case Studies

Real-world patterns observed in mature skill repositories.

### Case Study: A Mature CLI Skill Library

**Source:** A production skill library wrapping a CLI task-tracking tool (anonymized).

**Observed patterns:**

1. **Progressive disclosure is real:** Only frontmatter is loaded at discovery; SKILL body loads on invocation; resources require explicit reads.

2. **Resources are the DRY mechanism:** Heavy use of `resources/` to avoid duplication across skills. One refactor removed ~105 duplicated lines by extracting shared content.

3. **ADR pattern for architecture decisions:** Used ADR-0001 to justify "CLI output as source of truth" and keep SKILL.md small (~500 words vs original ~3,300).

4. **Two execution modes:** "Dispatching" (agent spawns subagents) vs "Advising" (human handles handoffs) as separate skills with shared resources.

5. **Gate labels as workflow control:** `needs-spec` blocks start, `needs-verification` blocks close. Skills check labels before proceeding.

**Why it works:**

- Separation of concerns: workflow logic in SKILL.md, reference content in resources
- DRY: shared resources updated once, used everywhere
- Explicit handoffs: skills reference sub-skills with `**REQUIRED SUB-SKILL:**` markers

**How to apply:**

- Audit your skills for duplicated blocks
- Extract stable content to `resources/`
- Use ADRs to document architectural decisions that affect skill structure

---

## Consensus & Disagreements

This section tracks where sources agree, disagree, or leave gaps.

### Strong Consensus (All Sources Agree)

| Practice | Notes |
|----------|-------|
| 500-line SKILL.md limit | Anthropic docs, Agent Skills spec, superpowers, community |
| Include WHAT and WHEN in descriptions | Agent Skills spec, Anthropic docs |
| Third-person for descriptions | Agent Skills spec, Anthropic docs (explicit), superpowers (implicit) |
| Progressive disclosure | All sources recommend lazy loading |
| One-level-deep references | Agent Skills spec, Anthropic docs |
| Test with real usage before finalizing | TDD-style development |
| Gerund naming convention (-ing verbs) | Anthropic docs, superpowers |
| Name must match directory name | Agent Skills spec |
| Evaluation-driven development | Anthropic docs (create evals before documentation) |

### Minor Disagreements

| Topic | Anthropic | Community | Notes |
|-------|-----------|-----------|-------|
| Description length | 1024 chars max | ~500 chars recommended | Community prefers brevity |
| Testing rigor | "Test with all models" | TDD with pressure scenarios | Community more rigorous |
| Point of view in body | Not specified | "You" for instructions | Superpowers more explicit |

### Open Questions (No Consensus)

| Question | Current Approaches |
|----------|-------------------|
| When to use `when_to_use` frontmatter field? | Undocumented; may be deprecated. Rely on `description` instead. |
| How to handle skill conflicts? | No standard pattern. User must manually resolve. |
| Skill versioning mid-project? | No standard pattern. Some use git tags. |
| Metrics for skill effectiveness? | Manual transcript analysis. No tooling. |

### Patterns Without Official Endorsement

These patterns appear in community sources but aren't in official Agent Skills spec or Anthropic docs:

- **Pressure testing with Cialdini principles** — superpowers only
- **Iron Laws / Red Flags sections** — superpowers only
- **Rationalization tables** — superpowers only
- **DOT flowcharts as executable logic** — superpowers only
- **DRY via CLI tools** — beads only

These are valuable but may not be required for simpler skills.

### Patterns Now Officially Endorsed

These patterns from community sources are now in official Anthropic docs:

- **Template pattern** — Provide output templates with strict vs flexible variants
- **Examples pattern** — Input/output pairs like regular prompting
- **Evaluation-driven development** — Create evals before documentation
- **Iterative development with Claude A/B** — Expert designs, user tests
- **Solve, don't punt** — Scripts handle errors explicitly
- **No voodoo constants** — All magic numbers must be justified

---

## CI Gates (Machine-Readable)

```yaml
turian_skills_ci_gates:
  max_dot_nodes: 8
  frontmatter_allowed_keys: ["name", "description", "license", "compatibility", "metadata", "allowed-tools"]
  required_sections: ["## Quick Reference", "## Failure Modes"]
  exempt_required_sections_directive: "<!-- validate: exempt-required-sections -->"
```

---

## Summary Checklist

### Core Quality

- [ ] Description includes both what the skill does AND when to use it
- [ ] Description is short (budget ~500 chars max)
- [ ] Description is written in third person
- [ ] Name uses gerund form or noun phrase (`processing-pdfs`, `pdf-processing`)
- [ ] Name matches parent directory name
- [ ] File is under 500 lines (split heavy content to `reference.md` if needed)
- [ ] Uses imperative "You MUST" language for mandatory steps
- [ ] Includes explicit STOP points for human approval
- [ ] Uses DOT notation or numbered steps for processes
- [ ] Structures as loops with re-entry, not linear one-shot
- [ ] References are progressively disclosed, not bulk-loaded
- [ ] File references are one level deep from SKILL.md
- [ ] Longer reference files (>100 lines) have table of contents
- [ ] Covers edge cases and failure modes, not just happy paths
- [ ] Red flags list addresses common rationalizations
- [ ] No time-sensitive information (or in "old patterns" section)
- [ ] Consistent terminology throughout

### Code and Scripts

- [ ] Scripts solve problems rather than punt to Claude
- [ ] Error handling is explicit and helpful
- [ ] No "voodoo constants" (all values justified)
- [ ] Required packages listed in instructions
- [ ] No Windows-style paths (all forward slashes)
- [ ] Validation/verification steps for critical operations
- [ ] Feedback loops included for quality-critical tasks
- [ ] Clear distinction between execute vs read as reference

### Testing

- [ ] At least three evaluations created before extensive documentation
- [ ] Watched an agent fail without the skill first (the "RED" test)
- [ ] Tested with "react todo list" smoke test
- [ ] Pressure-tested with adversarial scenarios
- [ ] Tested with Haiku, Sonnet, and Opus (if cross-model)
- [ ] Includes tool translation notes if cross-platform

### Key Principles

- One file, symlinked: Single source of truth, works with multiple tools
- Under 50 instructions: Quality degrades with instruction count
- Imperative language: Reduces ambiguity
- Repeat critical rules: Reinforces importance
- Explicit STOP points: Clearer than "wait for approval"
- Avoid tool-specific syntax: Maximum portability
- Test across models: Catch interpretation differences early

---

## Open Problems

These areas are not yet well-addressed in the ecosystem and require research:

### Technical

1. **Interrupt Handling:** Does `Ctrl+C` during a file write corrupt the state file? Do we need to implement atomic write wrappers (write to temp + rename) in the skill scripts?
2. **Script Environment Propagation:** Do environment variables (like `OPENAI_API_KEY`) pass through cleanly to `scripts/` in all environments (Codex vs OpenCode)? This determines if we can use Python scripts for heavy logic.
3. **Package availability:** Anthropic API has no network access and no runtime package installation. How do we handle skills that need external dependencies?

### Lifecycle

1. **Versioning skills:** What happens when a skill changes mid-project? No standard pattern exists. Some use git tags.
2. **Skill conflicts:** What if two skills give contradictory instructions? User must manually resolve.
3. **Skill deprecation:** How do you sunset a skill without breaking dependent workflows?

### Observability

1. **Skill debugging:** How do you know why a skill didn't trigger? No tooling exists.
2. **Metrics/observability:** How do you measure skill effectiveness over time? Manual transcript analysis only.
3. **Discovery visibility:** How do you verify which skills are actually in the system prompt? No tooling exists.

### Discovery

1. **`when_to_use` field:** This frontmatter field is extensively implemented but lacks official documentation. May be deprecated—rely on `description` instead.
2. **Semantic matching limits:** How does Claude's skill selection degrade with 100+ skills? No published benchmarks.

### Cross-Platform

1. **Tool mapping consistency:** How do you ensure `TodoWrite` → `update_plan` mappings work across Claude Code, OpenCode, and Codex?
2. **Platform-specific capabilities:** Some skills work on claude.ai (can install packages) but not API (no network). How do you document these constraints?

---

## Audit Checklist for Skills

Use this checklist when auditing skills in this repo:

### Structure
- [ ] Name matches parent directory name
- [ ] Name uses lowercase, numbers, hyphens only (no consecutive hyphens)
- [ ] Description includes both what + when
- [ ] Description is under 500 chars (prefer brevity)
- [ ] Description is written in third person
- [ ] Under 500 lines total
- [ ] File references are one level deep

### Content
- [ ] Progressive disclosure used for shared blocks (extract to `resources/`)
- [ ] STOP points are explicit
- [ ] Failure modes included
- [ ] Uses imperative "You MUST" language for mandatory steps
- [ ] Red flags list addresses common rationalizations
- [ ] No repo-specific paths hardcoded
- [ ] No time-sensitive information
- [ ] Consistent terminology

### Scripts (if applicable)
- [ ] Scripts handle errors explicitly (don't punt)
- [ ] No voodoo constants
- [ ] Uses forward slashes for paths
- [ ] Clear execute vs read distinction

---

## Related Documents

- **Tool-specific best practices:** [best-practices-for-using-beads.md](./best-practices-for-using-beads.md)
- **Repo-specific policies** belong in the consuming repo's `AGENTS.md` or `CLAUDE.md`, not in skill library docs.
