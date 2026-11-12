"""Synthetic CLI and regional matching tests (no real employers)."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from test_build import sample

SPEC = importlib.util.spec_from_file_location('directory_filter', Path(__file__).with_name('filter.py'))

class FilterTests(unittest.TestCase):
    def load_filter(self):
        assert SPEC is not None and SPEC.loader is not None
        module = importlib.util.module_from_spec(SPEC)
        SPEC.loader.exec_module(module)
        return module

    def rows(self):
        rows=[]
        for name, scope, countries in [('explicit','countries',['FR']), ('regional','eu_eea',[]), ('unknown','unknown',[])]:
            r=sample();r.update(id=name,name=name)
            r['eligibility']={'scope':scope,'countries':countries,'work_model':'fully_remote','restrictions':[], 'checked_at':'2026-11-02','sources':['https://example.org/careers']}
            rows.append(r)
        return rows

    def test_exact_vs_regional(self):
        mod=self.load_filter()
        result=mod.filter_rows(self.rows(),'FR')
        self.assertEqual([r['id'] for r in result['matches']],['explicit'])
        self.assertEqual(result['hints'],[])
        result=mod.filter_rows(self.rows(),'FR',include_regionals=True)
        self.assertEqual([r['id'] for r in result['hints']],['regional'])
        self.assertEqual(mod.filter_rows(self.rows(),'GB',include_regionals=True)['hints'],[])
        self.assertEqual(mod.filter_rows(self.rows(),'FR',work_model='hybrid',include_regionals=True),{'matches':[],'hints':[]})

    def test_cli_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'synthetic.json';path.write_text(json.dumps(self.rows()))
            command=[sys.executable,str(Path(__file__).with_name('filter.py')),'--country','FR','--work-model','fully_remote','--include-regionals','--file',str(path)]
            result=subprocess.run(command,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual([r['id'] for r in json.loads(result.stdout)['matches']],['explicit'])
            bad=subprocess.run(command+['--country','UK'],text=True,capture_output=True)
            self.assertNotEqual(bad.returncode,0)

if __name__=='__main__':unittest.main()
