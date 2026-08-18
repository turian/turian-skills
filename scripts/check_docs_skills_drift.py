#!/usr/bin/env python3
"""Check that validate_skills.py constants match docs/llm/best-practices-for-writing-skills.md"""
import sys
import re
import yaml
from pathlib import Path

# Import the constants from validate_skills
from validate_skills import (
    MAX_NODES,
    ALLOWED_FRONTMATTER_KEYS,
    REQUIRED_SECTIONS,
    EXEMPT_SECTIONS_DIRECTIVE,
)


def main():
    doc_path = Path('docs/llm/best-practices-for-writing-skills.md')
    content = doc_path.read_text()

    # Extract YAML block
    match = re.search(r'```yaml\nturian_skills_ci_gates:(.*?)```', content, re.DOTALL)
    if not match:
        print("HARD FAIL: No turian_skills_ci_gates YAML block found in docs")
        sys.exit(1)

    yaml_content = "turian_skills_ci_gates:" + match.group(1)
    doc_config = yaml.safe_load(yaml_content)['turian_skills_ci_gates']

    errors = []

    # Check each constant
    if MAX_NODES != doc_config['max_dot_nodes']:
        errors.append(f"MAX_NODES: code={MAX_NODES}, docs={doc_config['max_dot_nodes']}")

    if ALLOWED_FRONTMATTER_KEYS != set(doc_config['frontmatter_allowed_keys']):
        errors.append(f"ALLOWED_FRONTMATTER_KEYS: code={ALLOWED_FRONTMATTER_KEYS}, docs={set(doc_config['frontmatter_allowed_keys'])}")

    if set(REQUIRED_SECTIONS) != set(doc_config['required_sections']):
        errors.append(f"REQUIRED_SECTIONS: code={set(REQUIRED_SECTIONS)}, docs={set(doc_config['required_sections'])}")

    if EXEMPT_SECTIONS_DIRECTIVE != doc_config['exempt_required_sections_directive']:
        errors.append(f"EXEMPT_SECTIONS_DIRECTIVE: code={EXEMPT_SECTIONS_DIRECTIVE!r}, docs={doc_config['exempt_required_sections_directive']!r}")

    if errors:
        print("HARD FAIL: Docs/code drift detected:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("Docs and code are in sync")
    sys.exit(0)


if __name__ == '__main__':
    main()
