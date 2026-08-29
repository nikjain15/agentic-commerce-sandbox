#!/usr/bin/env python3
"""Check that every relative link in the repository's Markdown resolves.

Deliberately offline. An external link checker fails when somebody else's site
is down, which trains people to ignore a red build; this only checks links whose
target is inside the repository, so a failure is always our own broken
cross-reference and always worth fixing.

Exit 0 = clean; exit 1 = findings printed.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
FENCE = re.compile(r'^```.*?^```', re.MULTILINE | re.DOTALL)
CODE_SPAN = re.compile(r'`[^`\n]*`')
SKIP_PREFIX = ('http://', 'https://', 'mailto:', '#', 'tel:', 'data:')


def strip_code(text: str) -> str:
    """Remove fenced blocks and inline spans.

    A link inside backticks is documentation of a link's shape, not a link:
    `[Source Name, Year](URL)` in a style guide must not be reported as a
    broken path to a file named URL.
    """
    text = FENCE.sub('', text)
    return CODE_SPAN.sub('', text)

def main() -> int:
    problems = []
    checked = 0
    for md in sorted(ROOT.rglob('*.md')):
        if '.git' in md.parts or 'node_modules' in md.parts:
            continue
        text = strip_code(md.read_text(encoding='utf-8', errors='replace'))
        for raw in LINK.findall(text):
            target = raw.split()[0].strip()          # drop optional "title"
            if target.startswith(SKIP_PREFIX) or not target:
                continue
            path = target.split('#', 1)[0]           # anchor is not a file
            if not path:
                continue
            checked += 1
            resolved = (md.parent / path).resolve()
            if not resolved.exists():
                problems.append(f'{md.relative_to(ROOT)} -> {target}')
    if problems:
        print(f'{len(problems)} broken relative link(s):\n')
        for p in problems:
            print(f'  {p}')
        return 1
    print(f'OK - {checked} relative link(s) resolve.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
