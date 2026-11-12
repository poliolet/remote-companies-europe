"""Synthetic validation tests; no actual companies or network needed."""
import copy
import unittest
import build


def sample():
    return {'id':'example-company','name':'Example Company (synthetic fixture)','description':'Synthetic fixture used only to test the public directory validator.','category':'Synthetic','website':'https://example.org/','careers_url':'https://example.org/careers','remote_signal':'needs_verification','remote_note':'Synthetic test data, not an actual employer.','record_reviewed_at':'2026-11-02','public_sources_checked_at':'2026-11-02','sources':['https://example.org/'],'verification_note':'Synthetic fixture only.'}

class ValidationTests(unittest.TestCase):
    def test_valid(self):self.assertEqual(len(build.validate([sample()])),1)
    def test_private_field(self):
        s=sample();s['fit_for_pau']='private'
        with self.assertRaises(AssertionError):build.validate([s])
    def test_duplicates(self):
        with self.assertRaises(AssertionError):build.validate([sample(),sample()])
    def test_query_token(self):
        s=sample();s['website']='https://example.org/?token=private'
        with self.assertRaises(AssertionError):build.validate([s])
    def test_local_path(self):
        s=sample();s['description']='File /home/somebody/private'
        with self.assertRaises(AssertionError):build.validate([s])
    def test_email(self):
        s=sample();s['description']='Contact private@example.org'
        with self.assertRaises(AssertionError):build.validate([s])
    def test_bad_status(self):
        s=sample();s['remote_signal']='guaranteed_spain_jobs'
        with self.assertRaises(AssertionError):build.validate([s])
    def test_localhost(self):
        s=sample();s['website']='https://localhost/'
        with self.assertRaises(AssertionError):build.validate([s])
    def test_missing_homepage_caveat(self):
        s=sample();s['website']='';s['verification_note']=''
        with self.assertRaises(AssertionError):build.validate([s])

class EligibilityTests(unittest.TestCase):
    def row(self):
        r=sample()
        r['eligibility']={'scope':'countries','countries':['FR'],'work_model':'fully_remote','restrictions':[], 'checked_at':'2026-11-02','sources':['https://example.org/careers']}
        return r

    def test_unknown_defaults(self):
        r=sample();before=copy.deepcopy(r)
        self.assertEqual(build.eligibility(r),{'scope':'unknown','countries':[],'work_model':'unknown','restrictions':[],'checked_at':'','sources':[]})
        self.assertEqual(r,before)

    def test_valid_eligibility(self):build.validate([self.row()])

    def test_invalid_country(self):
        for code in ['UK','EU','ZZ','US','fr']:
            r=self.row();r['eligibility']['countries']=[code]
            with self.subTest(code=code),self.assertRaises(AssertionError):build.validate([r])

    def test_conflicts(self):
        for changes in [{'scope':'unknown'}, {'countries':[]}, {'checked_at':''}, {'sources':[]}, {'checked_at':'2026-02-30'}, {'sources':['https://example.org/?token=private']}, {'work_model':'remote'}, {'scope':'anywhere'}, {'extra':'no'}]:
            r=self.row();r['eligibility'].update(changes)
            with self.subTest(changes=changes),self.assertRaises(AssertionError):build.validate([r])

    def test_supported_codes_and_broad_scopes(self):
        for code in build.COUNTRIES:
            r=self.row();r['eligibility']['countries']=[code]
            with self.subTest(code=code):build.validate([r])
        for scope in ['europe','eu_eea','worldwide']:
            r=self.row();r['eligibility'].update(scope=scope,countries=[])
            with self.subTest(scope=scope):build.validate([r])
        r=self.row();r['eligibility'].update(scope='eu_eea',countries=['GB'])
        with self.assertRaises(AssertionError):build.validate([r])
        r=self.row();del r['eligibility']['restrictions']
        with self.assertRaises(AssertionError):build.validate([r])
        r=self.row();r['eligibility']['countries']=['FR','FR']
        with self.assertRaises(AssertionError):build.validate([r])

    def test_broad_requires_evidence(self):
        for scope in ['europe','eu_eea','worldwide']:
            r=self.row();r['eligibility'].update(scope=scope,countries=[],checked_at='')
            with self.subTest(scope=scope),self.assertRaises(AssertionError):build.validate([r])

    def test_nested_privacy(self):
        for value in ['/home/private','/Users/private','[[private]]','fit_for_pau','manual_status_lock','rejection_reason','private@example.org','ghp_abc','sk-secret']:
            for field in ['restrictions','sources']:
                r=self.row();r['eligibility'][field]=[value]
                with self.subTest(field=field,value=value),self.assertRaises(AssertionError):build.validate([r])
        r=self.row();r['sources']=['https://example.org/fit_for_pau']
        with self.assertRaises(AssertionError):build.validate([r])

    def test_generated_artifacts(self):
        import csv
        import io
        import json
        from pathlib import Path
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'data').mkdir()
            (root/'data/companies.json').write_text(json.dumps([sample(),dict(self.row(),id='confirmed',name='Confirmed synthetic')]))
            # Public documentation links exist in a real checkout.
            for filename in ['METHODOLOGY.md','CONTRIBUTING.md','LICENSE-DATA.md','LICENSE']:(root/filename).touch()
            with patch.object(build,'ROOT',root):build.main()
            self.assertIn('Scope:** unknown',(root/'companies/example-company.md').read_text())
            self.assertIn('Exact country matches',(root/'countries/FR.md').read_text())
            self.assertTrue((root/'countries/unknown.md').exists())
            self.assertTrue((root/'countries/countrycodes.md').exists())
            self.assertTrue((root/'countries/README.md').exists())
            self.assertTrue((root/'README.md').read_text().startswith('# Remote companies — Europe\n'))
            self.assertNotIn(b'\r\n',(root/'data/companies.csv').read_bytes())
            rows=list(csv.DictReader(io.StringIO((root/'data/companies.csv').read_text())))
            self.assertEqual(json.loads(rows[0]['eligibility_countries']),['FR'])
            self.assertEqual(rows[1]['eligibility_scope'],'unknown')

if __name__=='__main__':unittest.main(verbosity=2)
