"""Synthetic builds and isolated Git repositories; never read the live dataset."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import build
from test_build import sample

CHECK = Path(__file__).with_name('check_generated.py').resolve()


def prepare(root, rows):
    (root / 'data').mkdir(exist_ok=True)
    (root / 'data/companies.json').write_text(json.dumps(rows))
    for name in ['METHODOLOGY.md', 'CONTRIBUTING.md', 'LICENSE-DATA.md', 'LICENSE']:
        (root / name).touch()


def render(root):
    output = io.StringIO()
    with patch.object(build, 'ROOT', root), contextlib.redirect_stdout(output):
        build.main()
    return json.loads(output.getvalue())


class GeneratedChecksTests(unittest.TestCase):
    def git(self, root, *args):
        return subprocess.run(['git', '-C', str(root), *args], check=True,
                              capture_output=True, text=True)

    def initialize(self, root):
        self.git(root, 'init', '-q')
        self.git(root, 'config', 'user.name', 'Synthetic Test')
        self.git(root, 'config', 'user.email', 'synthetic@example.invalid')

    def commit(self, root):
        self.git(root, 'add', '.')
        self.git(root, 'commit', '-qm', 'Synthetic baseline')

    def check(self, root):
        return subprocess.run([sys.executable, str(CHECK)], cwd=root,
                              capture_output=True, text=True)

    def test_clean_repository_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.initialize(root)
            (root / 'README.md').write_text('synthetic\n')
            self.commit(root)
            result = self.check(root)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_rebuild_detects_untracked_country_missing_from_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prepare(root, [sample()])
            render(root)
            self.initialize(root)
            (root / 'countries/FR.md').unlink()
            self.commit(root)
            render(root)
            # This is precisely the case a tracked diff alone misses.
            self.git(root, 'diff', '--exit-code')
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('countries/FR.md', result.stdout)

    def test_tracked_and_staged_changes_report_paths_not_contents(self):
        for staged in [False, True]:
            with self.subTest(staged=staged), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.initialize(root)
                (root / 'README.md').write_text('baseline\n')
                self.commit(root)
                (root / 'README.md').write_text('DO_NOT_PRINT_CONTENTS\n')
                if staged:
                    self.git(root, 'add', 'README.md')
                result = self.check(root)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn('README.md', result.stdout)
                self.assertNotIn('DO_NOT_PRINT_CONTENTS', result.stdout + result.stderr)

    def test_git_failure_is_not_clean(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.check(Path(directory))
            self.assertNotEqual(result.returncode, 0)

    def test_removed_company_fails_closed_without_deleting_card(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            removed = dict(sample(), id='removed', name='Removed synthetic company')
            prepare(root, [sample(), removed])
            self.assertEqual(render(root)['cards'], 2)
            stale = root / 'companies/removed.md'
            original = stale.read_bytes()
            (root / 'data/companies.json').write_text(json.dumps([sample()]))
            output = io.StringIO()
            with patch.object(build, 'ROOT', root), contextlib.redirect_stdout(output):
                with self.assertRaisesRegex(AssertionError, 'Company card set mismatch'):
                    build.main()
            self.assertEqual(stale.read_bytes(), original)
            self.assertNotIn('"schema": "pass"', output.getvalue())


if __name__ == '__main__':
    unittest.main(verbosity=2)
