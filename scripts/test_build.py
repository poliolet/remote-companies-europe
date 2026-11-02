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

if __name__=='__main__':unittest.main(verbosity=2)
