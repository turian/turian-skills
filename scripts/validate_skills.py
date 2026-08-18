#!/usr/bin/env python3
"""Validate SKILL.md files against conventions. HARD FAIL on violations."""
import sys
import re
import yaml
import pydot
from pathlib import Path

MAX_NODES = 8
MIN_BODY_LENGTH = 100

# AgentSkills spec: name and description required, others optional
REQUIRED_FRONTMATTER_KEYS = {"name", "description"}
OPTIONAL_FRONTMATTER_KEYS = {"license", "compatibility", "metadata", "allowed-tools"}
ALLOWED_FRONTMATTER_KEYS = REQUIRED_FRONTMATTER_KEYS | OPTIONAL_FRONTMATTER_KEYS

REQUIRED_SECTIONS = ["## Quick Reference", "## Failure Modes"]

# Directive to exempt a skill from required sections check
# Must be placed immediately after frontmatter (first non-empty line)
EXEMPT_SECTIONS_DIRECTIVE = '<!-- validate: exempt-required-sections -->'


def has_exempt_directive(content: str) -> bool:
    """Check if exemption directive is in the required location (first non-empty line after frontmatter)."""
    # Find end of frontmatter
    match = re.match(r'^---\n.*?\n---\n?', content, re.DOTALL)
    if not match:
        return False

    # Get content after frontmatter
    after_frontmatter = content[match.end():]

    # Find first non-empty line
    for line in after_frontmatter.split('\n'):
        stripped = line.strip()
        if stripped:
            return stripped == EXEMPT_SECTIONS_DIRECTIVE

    return False


def validate_frontmatter(path: Path, content: str) -> list[str]:
    """Check frontmatter schema."""
    errors = []
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return ['No frontmatter found']

    try:
        fm = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        return [f'Invalid YAML: {e}']

    # Handle empty or non-dict frontmatter
    if not isinstance(fm, dict):
        return ['Frontmatter is empty or not a valid mapping']

    # Check required keys present
    missing = REQUIRED_FRONTMATTER_KEYS - set(fm.keys())
    if missing:
        errors.append(f'Missing required frontmatter keys: {missing}')

    # Check no unknown keys (only allow spec-defined keys)
    extra = set(fm.keys()) - ALLOWED_FRONTMATTER_KEYS
    if extra:
        errors.append(f'Unknown frontmatter keys: {extra}')

    # name format (AgentSkills spec)
    name = fm.get('name', '')
    if not name:
        errors.append('Name is missing')
    elif len(name) > 64:
        errors.append(f'Name too long: {len(name)} chars (max 64)')
    elif not re.match(r'^[a-z0-9-]+$', name):
        errors.append(f'Invalid name format (lowercase, numbers, hyphens only): {name!r}')
    elif name.startswith('-') or name.endswith('-'):
        errors.append(f'Name cannot start or end with hyphen: {name!r}')
    elif '--' in name:
        errors.append(f'Name cannot contain consecutive hyphens: {name!r}')
    else:
        # Check name matches directory
        expected_name = path.parent.name
        if name != expected_name:
            errors.append(f'Name {name!r} does not match directory {expected_name!r}')

    # description rules
    desc = fm.get('description', '')
    if not desc:
        errors.append('Description is missing')
    elif len(desc) > 1024:
        errors.append(f'Description too long: {len(desc)} chars (max 1024)')
    elif not desc.startswith('Use when'):
        errors.append('Description must start with "Use when"')
    elif ' you ' in desc.lower() or desc.lower().startswith('use when you'):
        # Catch "Use when you need..." which is second-person
        errors.append('Description must be third-person (avoid "you")')

    # Validate optional fields (AgentSkills spec)
    if 'license' in fm and not isinstance(fm['license'], str):
        errors.append('License must be a string')

    if 'compatibility' in fm:
        compat = fm['compatibility']
        if not isinstance(compat, str):
            errors.append('Compatibility must be a string')
        elif len(compat) > 500:
            errors.append(f'Compatibility too long: {len(compat)} chars (max 500)')

    if 'metadata' in fm and not isinstance(fm['metadata'], dict):
        errors.append('Metadata must be a mapping')

    if 'allowed-tools' in fm and not isinstance(fm['allowed-tools'], str):
        errors.append('Allowed-tools must be a string')

    return errors


def extract_dot_blocks(content: str) -> list[str]:
    """Extract ```dot fenced code blocks from markdown."""
    pattern = r'```dot\s*\n(.*?)```'
    return re.findall(pattern, content, re.DOTALL)


def count_nodes(dot_source: str) -> int:
    """Count nodes using pydot parser. Raises ValueError on parse failure."""
    # Wrap in digraph if not a complete graph (check for actual DOT header)
    # Regex matches: digraph name { or graph name { at start
    if not re.match(r'^\s*(di)?graph\s+\w*\s*\{', dot_source):
        dot_source = f'digraph G {{ {dot_source} }}'

    graphs = pydot.graph_from_dot_data(dot_source)
    if not graphs:
        raise ValueError('DOT parse failed')

    graph = graphs[0]

    # Get explicit nodes
    nodes = set()
    for node in graph.get_nodes():
        name = node.get_name().strip('"')
        # Skip special nodes
        if name not in ('node', 'edge', 'graph', '\\n', ''):
            nodes.add(name)

    # Also get nodes from edges (implicit nodes)
    for edge in graph.get_edges():
        src = edge.get_source().strip('"')
        dst = edge.get_destination().strip('"')
        if src and src not in ('node', 'edge', 'graph'):
            nodes.add(src)
        if dst and dst not in ('node', 'edge', 'graph'):
            nodes.add(dst)

    return len(nodes)


def validate_dot_nodes(path: Path, content: str) -> list[str]:
    """Check DOT diagram node count."""
    errors = []
    blocks = extract_dot_blocks(content)

    for i, block in enumerate(blocks):
        try:
            node_count = count_nodes(block)
            if node_count > MAX_NODES:
                errors.append(f'DOT diagram #{i+1} has {node_count} nodes (max {MAX_NODES})')
        except ValueError:
            errors.append(f'DOT diagram #{i+1} failed to parse (HARD FAIL)')

    return errors


def validate_not_empty(path: Path, content: str) -> list[str]:
    """Check skill has content beyond frontmatter."""
    body = re.sub(r'^---\n.*?\n---\n?', '', content, flags=re.DOTALL)
    if len(body.strip()) < MIN_BODY_LENGTH:
        return [f'Body too short: {len(body.strip())} chars (min {MIN_BODY_LENGTH})']
    return []


def validate_links(path: Path, content: str) -> list[str]:
    """Check referenced resources and skills exist."""
    errors = []
    skill_dir = path.parent
    skills_root = skill_dir.parent

    # Check ../resources/*.md links
    for match in re.finditer(r'\.\./resources/(\S+\.md)', content):
        target = (skill_dir / '..' / 'resources' / match.group(1)).resolve()
        if not target.exists():
            errors.append(f'Missing resource: {match.group(0)}')

    # Check REQUIRED SUB-SKILL references
    # Format: **REQUIRED SUB-SKILL:** Use `skill-name` or REQUIRED SUB-SKILL: `skill-name`
    pattern = r'REQUIRED SUB-SKILL.*?`([^`]+)`'
    for match in re.finditer(pattern, content, re.IGNORECASE):
        skill_name = match.group(1).strip()
        target = skills_root / skill_name / 'SKILL.md'
        if not target.exists():
            errors.append(f'Missing required sub-skill: {skill_name}')

    return errors


def validate_required_sections(path: Path, content: str) -> list[str]:
    """Check workflow skills have required sections (Quick Reference + Failure Modes)."""
    # Skip if skill has the exemption directive in the required location
    if has_exempt_directive(content):
        return []

    errors = []

    # Check for each required section heading
    for section in REQUIRED_SECTIONS:
        # Build pattern to match exactly this heading (no trailing content except whitespace)
        pattern = rf'^{re.escape(section)}\s*$'
        if not re.search(pattern, content, re.MULTILINE):
            errors.append(f'Missing required section: {section}')

    return errors


def validate_skill(path: Path) -> list[str]:
    """Run all validations on a skill."""
    content = path.read_text(encoding='utf-8')
    errors = []
    errors.extend(validate_frontmatter(path, content))
    errors.extend(validate_dot_nodes(path, content))
    errors.extend(validate_not_empty(path, content))
    errors.extend(validate_links(path, content))
    errors.extend(validate_required_sections(path, content))
    return errors


def main():
    skills_dir = Path('skills')
    failed = False

    for skill_md in sorted(skills_dir.glob('*/SKILL.md')):
        errors = validate_skill(skill_md)
        skill_name = skill_md.parent.name

        if errors:
            print(f'✗ HARD FAIL: {skill_name}')
            for err in errors:
                print(f'  - {err}')
            failed = True
        else:
            print(f'✓ {skill_name}')

    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
