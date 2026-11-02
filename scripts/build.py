#!/usr/bin/env python3
"""Validate and render the curated PUBLIC dataset. No private inputs or network."""
import csv
import io
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {'id','name','description','category','website','careers_url','remote_signal','remote_note','record_reviewed_at','public_sources_checked_at','sources','verification_note'}
SIGNALS = ('spain_remote_signal','europe_remote_signal','global_remote_signal','mixed_or_restricted','needs_verification')
LABELS = {'spain_remote_signal':'Spain remote signal','europe_remote_signal':'Europe / EMEA remote signal','global_remote_signal':'Global / distributed signal','mixed_or_restricted':'Hybrid or country-restricted evidence','needs_verification':'Needs verification'}

def url(value):
    p=urlsplit(value)
    assert p.scheme=='https' and p.hostname and not p.username and not p.password, value
    assert not p.query, 'Do not publish query strings'
    assert not re.search(r'localhost|127\.0\.0\.1|^10\.|^192\.168\.',p.hostname),value

def validate(rows):
    assert rows and isinstance(rows,list)
    names=set();ids=set()
    for r in rows:
        assert set(r)==FIELDS, (r.get('name'),set(r)^FIELDS)
        assert r['id'] not in ids and r['name'].casefold() not in names
        ids.add(r['id']);names.add(r['name'].casefold())
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',r['id'])
        assert r['remote_signal'] in SIGNALS
        assert r['name'] and r['description'] and r['category']
        for k in ['website','careers_url']:
            if r[k]:url(r[k])
        assert r['website'] or r['verification_note'], 'Missing homepage needs explicit limitation'
        assert r['sources']
        for s in r['sources']:url(s)
        for v in r.values():
            if isinstance(v,str):
                assert not re.search(r'/home/|/Users/|\[\[|fit_for_pau|manual_status_lock|rejection_reason|@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|gh[pousr]_[A-Za-z0-9]|sk-[A-Za-z0-9]',v), 'Private content or secret-like data'
        for k in ['record_reviewed_at','public_sources_checked_at']:
            assert not r[k] or re.fullmatch(r'\d{4}-\d{2}-\d{2}',r[k]),(r['name'],k,r[k])
    return rows

def main():
    rows=validate(json.loads((ROOT/'data/companies.json').read_text()))
    rows=sorted(rows,key=lambda x:x['name'].casefold())
    counts=Counter(r['remote_signal'] for r in rows)
    lines=['# Remote companies — Europe & Spain','',f'A public, source-linked directory of **{len(rows)} companies** for people researching remote-friendly work in Europe, with particular attention to Spain.','',
    '**This is a research directory, not a guarantee of current vacancies or eligibility.** Some entries have only historical signals, mixed hybrid policies or country restrictions. Always read the actual vacancy and confirm employment country, office attendance, timezone and contract terms. “Remote” does not mean “work from any country”.','',
    '## Browse','', '- [Alphabetical company profiles](companies/README.md)', '- [JSON dataset](data/companies.json)', '- [CSV dataset](data/companies.csv)', '- [Methodology and status definitions](METHODOLOGY.md)', '- [Contribute a correction or company](CONTRIBUTING.md)','',
    '## Evidence signals','', '*These labels summarize historical research signals, not freshly verified company-wide policies.*','']
    for s in SIGNALS:
        if counts[s]:lines.append(f'- **{LABELS[s]}:** {counts[s]}')
    lines+=['','## Company directory','','| Company | What it does | Remote signal | Links |','| --- | --- | --- | --- |']
    index=['# Companies','', '[Back to directory](../README.md)','']
    companydir=ROOT/'companies';companydir.mkdir(exist_ok=True)
    for r in rows:
        web=f"[Website]({r['website']})" if r['website'] else 'Website unverified'
        careers=f"[Careers]({r['careers_url']})" if r['careers_url'] else 'Careers source unverified'
        desc=r['description'].replace('|','/').replace('\n',' ')
        lines.append(f"| [{r['name']}](companies/{r['id']}.md) | {desc} | {LABELS[r['remote_signal']]} | {web} · {careers} |")
        index.append(f"- [{r['name']}]({r['id']}.md) — {r['category']}")
        card=[f"# {r['name']}",'',r['description'],'',f"- **Category:** {r['category']}",f"- **Website:** {web}",f"- **Jobs / careers:** {careers}",f"- **Historical remote signal:** {LABELS[r['remote_signal']]}",'',r['remote_note'],'',f"- **Historical record reviewed:** {r['record_reviewed_at'] or 'Not recorded'}",f"- **Public-source research date:** {r['public_sources_checked_at'] or 'Not verified'}"]
        if r['verification_note']:card+=['', '## Verification caveat','',r['verification_note']]
        card+=['','## Sources','']+[f'- {s}' for s in r['sources']]+['','Country eligibility, current openings and attendance requirements must be checked for the individual role.','', '[Back to directory](../README.md)','']
        (companydir/(r['id']+'.md')).write_text('\n'.join(card))
    (ROOT/'README.md').write_text('\n'.join(lines)+'\n\n## License\n\nOriginal directory data and editorial descriptions: [CC BY 4.0](LICENSE-DATA.md). Build/validation code: [MIT](LICENSE). Company names, trademarks and linked material remain their respective owners’ property.\n')
    (companydir/'README.md').write_text('\n'.join(index)+'\n')
    out=io.StringIO();fields=['id','name','description','category','website','careers_url','remote_signal','remote_note','record_reviewed_at','public_sources_checked_at','verification_note','sources'];w=csv.DictWriter(out,fieldnames=fields);w.writeheader()
    for r in rows:w.writerow({**r,'sources':' ; '.join(r['sources'])})
    (ROOT/'data/companies.csv').write_text(out.getvalue())
    for f in ROOT.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',f.read_text()):
            if '://' not in target and not target.startswith('#'):assert (f.parent/target.split('#')[0]).exists(),(f,target)
    print(json.dumps({'companies':len(rows),'cards':len(list(companydir.glob('*.md')))-1,'signals':dict(counts),'local_links':'pass','schema':'pass'}))

if __name__=='__main__':main()
