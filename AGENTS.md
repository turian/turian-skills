# Agent Instructions

## Local Dogfooding Setup

To develop skills using the skills themselves, link the source directories into your local config. This allows you to edit the source files while the agent uses them.

```bash
# 1. Create the real directory (so it can hold multiple libraries if needed)
mkdir -p .claude/skills

# 2. Link the individual skills from the root directory
# Note: We use relative paths so the links work inside .claude/skills/
ln -s ../../skills/* .claude/skills/
```

**Note:** If you add a new skill folder to the repo, you must re-run the `ln` command to register it.

**Caveat:** If you break a skill while using it, you may need to manually fix the file or start a fresh session.

## Reference Documents

- [Best Practices for Writing Skills](docs/llm/best-practices-for-writing-skills.md) — tool-agnostic skill authoring

## Validation

**Golden path:** `make validate` is the single source of truth.

- Pre-push hook runs `make validate`
- GitHub CI runs `make validate`
- Run `make validate` before pushing

Install the pre-push hook:

```bash
make install-hooks
```

## CI Gates

All PRs must pass these checks (HARD FAIL):

| Check | Rule |
|-------|------|
| Frontmatter schema | Exactly `name` + `description`, third-person, starts with "Use when" |
| DOT node cap | ≤8 nodes per diagram |
| Resource links | Referenced resources/skills must exist |
| No empty skills | SKILL.md must have content beyond frontmatter |
| Markdown lint | Must pass markdownlint |

## Language Preferences

**Prefer Python to Bash** for CI scripts unless Bash is significantly more ergonomic.

| Language | Use for |
|----------|---------|
| Python | Scripts with parsing, regex, or growth potential; CI lint checks |
| Bash | One-liners in Makefile; simple file ops; git commands |

## Python Package Management

**Use `uv`** for all Python package management. Never use:

- `pip` or `pip3`
- `venv` or `python -m venv`
- `uv venv` or `uv pip`

Just use `uv` directly:

```bash
uv run python script.py      # Run with dependencies
uv sync                      # Install from pyproject.toml
```

## Make Targets

This repo keeps Make targets minimal. Only three user-facing targets:

| Target | Purpose |
|--------|---------|
| `make validate` | Golden path - run all checks (CI and pre-push use this) |
| `make fix` | Auto-fix markdown where possible |
| `make install-hooks` | Install pre-push hook |

Do not add new Make targets unless user-facing and broadly necessary. Prefer adding checks to `make validate`.

## No Fallbacks

**HARD FAIL, no fallbacks.** If a dependency is missing or a check cannot run properly, the script must error - not silently degrade to a less accurate method.

- If `pydot` is not installed, `validate_skills.py` crashes (correct)
- If a file can't be parsed, error (don't skip it)
- If a check is ambiguous, fail loudly and fix the check

Fallbacks hide bugs and create false confidence.

## Pre-push Hook with core.hooksPath

If your repo uses `core.hooksPath` (check with `git config --get core.hooksPath`), the `make install-hooks` command will skip installation to avoid conflicts.

In this case, manually add the pre-push hook to your hooks directory:

```bash
# Add to your core.hooksPath directory
cat > "$(git config --get core.hooksPath)/pre-push" << 'EOF'
#!/bin/bash
set -e
make validate
EOF
chmod +x "$(git config --get core.hooksPath)/pre-push"
```
