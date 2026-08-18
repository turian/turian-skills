# Cross-Agent Skill Placement

Where a skill has to sit so both Claude Code and Codex load it, and what makes
one file work in both instead of two files drifting apart.

## Discovery paths

Neither host reads the other's directory.

| Scope | Claude Code | Codex |
| --- | --- | --- |
| Project | `.claude/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` |
| Search | Start dir up to repo root | CWD up to repo root |
| Personal | `~/.claude/skills/` | `~/.codex/skills/`, `~/.agents/skills/` |
| Symlinks | Followed | Followed |

`.codex/skills` as a Codex-private project directory was requested and closed as
not planned; `.agents/skills` is the sanctioned shared convention. Claude Code
has no equivalent — it reads `.claude/skills/` and nothing else.

Both hosts follow symlinks and both scan upward to the repo root, which is what
makes one canonical copy possible.

## The layout

Canonical file in `.agents/skills/`, relative symlink from `.claude/skills/`:

```text
.agents/skills/check-arrivals/SKILL.md
.claude/skills/check-arrivals -> ../../.agents/skills/check-arrivals
```

```bash
mkdir -p .agents/skills/<name> .claude/skills
ln -s ../../.agents/skills/<name> .claude/skills/<name>
```

Git stores symlinks natively, so this survives clone and works unchanged in every
worktree. Claude Code loads a target once even when it is reachable from two
locations, so the link cannot produce a duplicate.

For personal skills, the same idea with two links into a library checkout:

```bash
ln -s ~/dev/<library>/skills/<name> ~/.claude/skills/<name>
ln -s ~/dev/<library>/skills/<name> ~/.codex/skills/<name>
```

`~/.agents/skills/` reaches Codex but not Claude, so linking both explicit
directories is the arrangement that actually covers both.

## The directory name is the name

Claude derives the invocation name from the **directory** and treats frontmatter
`name` as a display label only. Codex derives it from **frontmatter `name`**.

When they disagree the skill answers to a different name in each host. Make them
identical — the Agent Skills spec requires it, and lowercase letters, digits, and
hyphens are all it permits. A colon in `name` is spec-invalid and splits the
skill across hosts.

## One file, not two

Two things tempt a second copy. Only one of them is real.

**The sigil is not a reason.** Claude spells invocation `/name`, Codex `$name`. A
body that says "invoke the arrivals skill" serves both. A body that hardcodes
either one guarantees a fork, and the fork is where the drift lands — the two
copies stop agreeing about the procedure, not about the punctuation.

**Capability differences are a reason.** Claude can hand work to a background
task and report later; Codex runs inline. That is a genuine behavioral fork.
Confine it to a marked block rather than duplicating the whole file, so the
shared 90 percent stays shared.

**Plugin namespacing is a reason.** A Claude plugin supplies its own prefix, so
its skill directories are unprefixed while the Codex copies need the prefix baked
into the name. Two names for two packaging models, not two procedures.

## Frontmatter

```yaml
---
name: check-arrivals
description: Use when …
metadata:
  turian.authored-by: "claude-opus-5"
  turian.authored-at: "2026-08-18"
  turian.review-status: "unreviewed"
---
```

`name` and `description` are the portable core — both hosts load them at startup
and nothing else until the skill fires. Keep host-specific frontmatter out of a
shared skill; the other host ignores it at best.

`metadata` is an arbitrary string-keyed, string-valued map in the spec, meant for
properties the spec does not define. Codex's own bundled skills use it, so it
survives the round trip. Values must be strings — `review-status: "unreviewed"`,
never a bare boolean.

An agent that authors a skill records the model and sets
`turian.review-status: "unreviewed"`. A human flips it to `"reviewed"`. Nothing
enforces this: the reference validator checks only top-level frontmatter keys and
never inspects inside `metadata`. It is a label, and git is the audit trail.

Note that `metadata` does not load until the skill activates. If an unreviewed
skill firing would actually cost something, the warning has to go in
`description`, which is the only field read up front.

## Validating

```bash
uv run skills-ref validate <skill-dir>    # from ~/dev/agentskills/skills-ref
```

This catches the name/directory mismatch, which is the failure that silently
produces a skill that works in one host and is missing from the other.
