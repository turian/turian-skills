# Turian Skills

Personal skills library for Claude Code.

## Quickstart

```bash
# Add skills to your project
mkdir -p .claude/skills
ln -s /path/to/turian-skills/skills/* .claude/skills/
```

## Development

```bash
# Install dependencies
uv sync

# Run validation
make validate

# Auto-fix markdown
make fix

# Run tests
make test

# Install pre-push hook
make install-hooks
```

## Adding a New Skill

1. Create `skills/<skill-name>/SKILL.md`
2. Add frontmatter with `name` and `description`
3. Description must start with "Use when" and be third-person
4. Include `## Quick Reference` and `## Failure Modes` sections
5. Run `make validate` to check

## Structure

```text
skills/
  my-skill/
    SKILL.md           # Core logic (required)
    reference.md       # Heavy docs (optional)
    scripts/           # Executable helpers
docs/
  llm/
    best-practices-for-writing-skills.md
scripts/
  validate_skills.py
  check_docs_skills_drift.py
tests/
  test_validate_skills.py
```

## License

MIT
