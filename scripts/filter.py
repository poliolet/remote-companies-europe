#!/usr/bin/env python3
"""Filter public eligibility; regional scope never becomes an exact country match."""
import argparse
import json
from pathlib import Path
from build import COUNTRIES, ROOT, WORK_MODELS, eligibility, regional_hint, validate


def filter_rows(rows, country, work_model=None, include_regionals=False):
    assert country in COUNTRIES, 'Use an assigned European ISO alpha-2 code (GB, not UK)'
    assert work_model is None or work_model in WORK_MODELS
    result={'matches':[], 'hints':[]}
    for row in sorted(validate(rows),key=lambda r:r['name'].casefold()):
        e=eligibility(row)
        if work_model is not None and e['work_model'] != work_model:continue
        if country in e['countries']:result['matches'].append(row)
        elif include_regionals and regional_hint(row,country):result['hints'].append(row)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--country',required=True,choices=sorted(COUNTRIES))
    parser.add_argument('--work-model',choices=WORK_MODELS)
    parser.add_argument('--include-regionals',action='store_true',help='Include separate, unconfirmed regional hints')
    parser.add_argument('--file',type=Path,default=ROOT/'data/companies.json',help='Public JSON input (default: repository dataset)')
    args=parser.parse_args()
    try:
        rows=json.loads(args.file.read_text())
        result=filter_rows(rows,args.country,args.work_model,args.include_regionals)
    except (OSError, ValueError, AssertionError) as exc:parser.error(str(exc))
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
