#!/usr/bin/env python3
"""Unit tests for validate_skills.py"""
from pathlib import Path

import pytest

from validate_skills import (
    extract_dot_blocks,
    count_nodes,
    validate_frontmatter,
    has_exempt_directive,
)


def test_extract_dot_blocks_finds_blocks():
    content = '''
Some text
```dot
digraph G { a -> b }
```
More text
'''
    blocks = extract_dot_blocks(content)
    assert len(blocks) == 1
    assert 'digraph G' in blocks[0]


def test_extract_dot_blocks_empty():
    content = 'No dot blocks here'
    blocks = extract_dot_blocks(content)
    assert len(blocks) == 0


def test_count_nodes_simple():
    dot = 'digraph G { a -> b -> c }'
    assert count_nodes(dot) == 3


def test_count_nodes_with_labels():
    dot = 'digraph G { a -> b [label="test"]; b -> c }'
    assert count_nodes(dot) == 3


def test_validate_frontmatter_valid():
    content = '''---
name: test-skill
description: Use when testing validation
---
Body content here
'''
    errors = validate_frontmatter(Path('skills/test-skill/SKILL.md'), content)
    assert len(errors) == 0


def test_validate_frontmatter_missing_use_when():
    content = '''---
name: test-skill
description: This does something
---
Body
'''
    errors = validate_frontmatter(Path('skills/test-skill/SKILL.md'), content)
    assert any('Use when' in e for e in errors)


def test_validate_frontmatter_with_optional_fields():
    """AgentSkills spec allows optional fields: license, compatibility, metadata, allowed-tools."""
    content = '''---
name: test-skill
description: Use when testing optional fields
license: MIT
compatibility: Requires Python 3.10+
metadata:
  author: test-org
  version: "1.0"
allowed-tools: Bash(git:*) Read Write
---
Body content here
'''
    errors = validate_frontmatter(Path('skills/test-skill/SKILL.md'), content)
    assert len(errors) == 0


def test_validate_frontmatter_rejects_unknown_fields():
    """Unknown fields should still be rejected."""
    content = '''---
name: test-skill
description: Use when testing unknown fields
unknown_field: should fail
---
Body
'''
    errors = validate_frontmatter(Path('skills/test-skill/SKILL.md'), content)
    assert any('Unknown frontmatter keys' in e for e in errors)


def test_validate_frontmatter_missing_required():
    """Missing required fields should fail."""
    content = '''---
name: test-skill
license: MIT
---
Body
'''
    errors = validate_frontmatter(Path('skills/test-skill/SKILL.md'), content)
    assert any('Missing required frontmatter keys' in e for e in errors)


# Name validation tests (AgentSkills spec)
def test_validate_frontmatter_name_leading_hyphen():
    """Name starting with hyphen should fail."""
    content = '''---
name: -bad-name
description: Use when testing
---
Body
'''
    errors = validate_frontmatter(Path('skills/-bad-name/SKILL.md'), content)
    assert any('cannot start or end with hyphen' in e for e in errors)


def test_validate_frontmatter_name_trailing_hyphen():
    """Name ending with hyphen should fail."""
    content = '''---
name: bad-name-
description: Use when testing
---
Body
'''
    errors = validate_frontmatter(Path('skills/bad-name-/SKILL.md'), content)
    assert any('cannot start or end with hyphen' in e for e in errors)


def test_validate_frontmatter_name_consecutive_hyphens():
    """Name with consecutive hyphens should fail."""
    content = '''---
name: bad--name
description: Use when testing
---
Body
'''
    errors = validate_frontmatter(Path('skills/bad--name/SKILL.md'), content)
    assert any('consecutive hyphens' in e for e in errors)


def test_validate_frontmatter_name_directory_mismatch():
    """Name not matching directory should fail."""
    content = '''---
name: wrong-name
description: Use when testing
---
Body
'''
    errors = validate_frontmatter(Path('skills/actual-name/SKILL.md'), content)
    assert any('does not match directory' in e for e in errors)


# Optional field type validation tests
def test_validate_frontmatter_compatibility_too_long():
    """Compatibility over 500 chars should fail."""
    content = f'''---
name: test-skill
description: Use when testing
compatibility: {"x" * 501}
---
Body
'''
    errors = validate_frontmatter(Path('skills/test-skill/SKILL.md'), content)
    assert any('Compatibility too long' in e for e in errors)


def test_validate_frontmatter_metadata_wrong_type():
    """Metadata must be a mapping."""
    content = '''---
name: test-skill
description: Use when testing
metadata: "not a mapping"
---
Body
'''
    errors = validate_frontmatter(Path('skills/test-skill/SKILL.md'), content)
    assert any('Metadata must be a mapping' in e for e in errors)


def test_validate_frontmatter_license_wrong_type():
    """License must be a string."""
    content = '''---
name: test-skill
description: Use when testing
license:
  - MIT
  - Apache
---
Body
'''
    errors = validate_frontmatter(Path('skills/test-skill/SKILL.md'), content)
    assert any('License must be a string' in e for e in errors)


def test_validate_frontmatter_allowed_tools_wrong_type():
    """Allowed-tools must be a string."""
    content = '''---
name: test-skill
description: Use when testing
allowed-tools:
  - Bash
  - Read
---
Body
'''
    errors = validate_frontmatter(Path('skills/test-skill/SKILL.md'), content)
    assert any('Allowed-tools must be a string' in e for e in errors)


def test_has_exempt_directive_valid_location():
    """Directive immediately after frontmatter should exempt."""
    content = '''---
name: test-skill
description: Use when testing
---

<!-- validate: exempt-required-sections -->

# Title
'''
    assert has_exempt_directive(content) is True


def test_has_exempt_directive_in_example_block():
    """Directive inside example block should NOT exempt."""
    content = '''---
name: test-skill
description: Use when testing
---

# Title

To exempt a skill, add this directive:

```markdown
<!-- validate: exempt-required-sections -->
```
'''
    assert has_exempt_directive(content) is False


def test_has_exempt_directive_later_in_file():
    """Directive later in file (not first non-empty line) should NOT exempt."""
    content = '''---
name: test-skill
description: Use when testing
---

# Title

<!-- validate: exempt-required-sections -->
'''
    assert has_exempt_directive(content) is False
