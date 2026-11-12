#!/usr/bin/env python3
"""Fail if rebuilding dirties a clean CI checkout, including untracked files.

Check the entire repository (tracked, staged and non-ignored untracked files).
Run from the checkout root after build.py. Diagnostics contain paths, not diffs.
"""
import json
import os
import subprocess
import sys


def main():
    result = subprocess.run(
        ['git', 'status', '--porcelain=v1', '-z', '--untracked-files=all', '--no-renames'],
        capture_output=True,
    )
    if result.returncode:
        print('Unable to check repository cleanliness.', file=sys.stderr)
        return 2
    entries = [entry for entry in result.stdout.split(b'\0') if entry]
    if entries:
        print('Repository differs after rebuild (paths only):')
        for entry in entries:
            # NUL-delimited porcelain preserves spaces/newlines; JSON quoting
            # prevents unusual filenames from injecting terminal/log controls.
            print(json.dumps(os.fsdecode(entry[3:]), ensure_ascii=True))
        return 1
    print('Repository clean after rebuild.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
