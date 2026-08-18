.PHONY: validate fix install-hooks test

# Rules to disable (permissive config matching existing .markdownlint.json behavior)
PYMARKDOWN_DISABLE = md003,md009,md012,md013,md019,md022,md024,md026,md027,md031,md033,md036,md041

# Markdown paths to lint (explicit to avoid .venv, .aider, etc.)
MD_PATHS = docs skills *.md

# Golden path - run all checks (CI and pre-push use this)
validate:
	uv run pymarkdown -d $(PYMARKDOWN_DISABLE) scan -r $(MD_PATHS)
	uv run python scripts/validate_skills.py
	uv run python scripts/check_docs_skills_drift.py
	@echo '✓ All validations passed'

# Auto-fix markdown where possible
fix:
	uv run pymarkdown -d $(PYMARKDOWN_DISABLE) fix -r $(MD_PATHS)

# Install pre-push hook
install-hooks:
	@if [ -n "$$(git config --get core.hooksPath)" ]; then \
		echo 'WARNING: core.hooksPath is set, skipping hook install'; \
	else \
		mkdir -p .git/hooks; \
		cp scripts/git-hooks/pre-push .git/hooks/pre-push; \
		chmod +x .git/hooks/pre-push; \
		echo '✓ Pre-push hook installed'; \
	fi

# Run tests
test:
	uv run --extra test pytest tests/ -v
