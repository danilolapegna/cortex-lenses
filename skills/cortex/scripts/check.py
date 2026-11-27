#!/usr/bin/env python3
"""Validate the skill's flat frontmatter and editable Markdown cards (Python 3.10+)."""
import argparse
import json
from pathlib import Path
import re
import sys

FAMILIES = {
    'reframe', 'challenge-a-premise', 'transfer-a-mechanism',
    'change-representation', 'find-leverage', 'generate', 'verify', 'decide',
    'model-an-opponent', 'manage-uncertainty', 'reverse-a-disadvantage',
}


def frontmatter(path):
    """Read a deliberately small YAML subset: flat string and boolean scalars.

    JSON double-quoted strings are also valid YAML. Quote strings with colons,
    hashes or YAML punctuation; multiline values and nested mappings are rejected.
    """
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    if not lines or lines[0] != '---':
        raise ValueError(f'{path}: missing opening frontmatter delimiter')
    try:
        end = lines.index('---', 1)
    except ValueError:
        raise ValueError(f'{path}: missing closing frontmatter delimiter') from None
    fields = {}
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        match = re.fullmatch(r'([a-z][a-z_-]*):[ \t]+(.+)', line)
        if not match:
            raise ValueError(f'{path}:{number}: expected key: scalar value')
        key, raw = match.groups()
        raw = raw.strip()
        if key in fields:
            raise ValueError(f'{path}:{number}: duplicate field {key}')
        if raw in {'true', 'false'}:
            value = raw == 'true'
        elif raw.startswith('"'):
            try:
                value = json.loads(raw)
            except ValueError as exc:
                raise ValueError(f'{path}:{number}: invalid quoted scalar: {exc}') from None
            if not isinstance(value, str):
                raise ValueError(f'{path}:{number}: expected a string')
        elif raw.startswith("'"):
            if not re.fullmatch(r"'(?:[^']|'')*'", raw):
                raise ValueError(f'{path}:{number}: invalid single-quoted scalar')
            value = raw[1:-1].replace("''", "'")
        else:
            if (raw[0] in '-?:,[]{}&*!|>\'%@`' or ': ' in raw or ' #' in raw
                    or raw.lower() in {'null', '~', 'yes', 'no', 'on', 'off'}
                    or re.match(r'^[+\-]?[0-9]', raw)):
                raise ValueError(f'{path}:{number}: quote this string scalar')
            value = raw
        fields[key] = value
    return fields, '\n'.join(lines[end + 1:])


def required_text(fields, keys, path):
    for key in keys:
        if not isinstance(fields.get(key), str) or not fields[key].strip():
            raise ValueError(f'{path}: missing or empty string field {key}')


def validate(root):
    entry = root / 'SKILL.md'
    fields, _ = frontmatter(entry)
    required_text(fields, ('name', 'description'), entry)
    if fields['name'] != root.name or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', fields['name']):
        raise ValueError(f'{entry}: name must match skill directory {root.name!r} in kebab-case')
    if len(fields['name']) > 64 or len(fields['description']) > 1024:
        raise ValueError(f'{entry}: name exceeds 64 or description exceeds 1024 characters')
    lenses = sorted((root / 'lenses').glob('*.md'))
    checks = sorted((root / 'checks').glob('*.md'))
    names = set()
    cores = 0
    for path in lenses:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', path.stem):
            raise ValueError(f'{path}: filename must be kebab-case')
        fields, body = frontmatter(path)
        required_text(fields, ('name', 'family', 'question'), path)
        if fields['family'] not in FAMILIES:
            raise ValueError(f'{path}: unknown family {fields["family"]!r}')
        if type(fields.get('core')) is not bool:
            raise ValueError(f'{path}: core must be true or false')
        normalized = fields['name'].casefold()
        if normalized in names:
            raise ValueError(f'{path}: duplicate lens name {fields["name"]!r}')
        names.add(normalized)
        cores += fields['core']
        headings = ('Steps', 'Use it when', 'Leave it out when')
        for heading in headings:
            match = re.search(r'^## ' + re.escape(heading) + r'\n+(.*?)(?=\n## |\Z)', body, re.M | re.S)
            if not match or not match[1].strip():
                raise ValueError(f'{path}: missing or empty {heading} section')
        steps = re.search(r'^## Steps\n+(.*?)(?=\n## |\Z)', body, re.M | re.S)[1]
        numbers = [int(x) for x in re.findall(r'^(\d+)\. \S', steps, re.M)]
        if len(numbers) not in {3, 4, 5} or numbers != list(range(1, len(numbers) + 1)):
            raise ValueError(f'{path}: Steps must contain 3–5 consecutively numbered steps')
        intro = body.split('## Steps', 1)[0]
        if not any(line.strip() and not line.startswith('#') for line in intro.splitlines()):
            raise ValueError(f'{path}: missing explanation before Steps')
    if cores < 24:
        raise ValueError(f'{root / "lenses"}: expected at least 24 core lenses, found {cores}')
    if not 6 <= len(checks) <= 10:
        raise ValueError(f'{root / "checks"}: expected 6–10 checks, found {len(checks)}')
    for path in checks:
        fields, body = frontmatter(path)
        required_text(fields, ('name', 'risk', 'check'), path)
        for heading in ('What can go wrong', 'How to check'):
            match = re.search(r'^## ' + heading + r'\n+(.*?)(?=\n## |\Z)', body, re.M | re.S)
            if not match or not match[1].strip():
                raise ValueError(f'{path}: missing or empty {heading} section')
    for mode in ('quick.md', 'full.md'):
        path = root / mode
        if not path.is_file() or len(path.read_text().splitlines()) >= 80:
            raise ValueError(f'{path}: mode must exist and have fewer than 80 lines')
    return len(lenses), cores, len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        total, cores, checks = validate(args.skill)
    except (OSError, ValueError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    print(f'PASS: {total} lenses ({cores} core, {total - cores} additional), {checks} checks; Agent Skills name and description valid')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
