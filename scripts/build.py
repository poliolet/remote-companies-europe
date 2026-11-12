#!/usr/bin/env python3
"""Validate and render the curated PUBLIC dataset. No private inputs or network."""
import csv
import io
import json
import re
from collections import Counter
from datetime import date

# European countries, including transcontinental states and Cyprus; ISO 3166-1
# assigned codes only (GB, not UK; Kosovo has no assigned ISO alpha-2 code).
COUNTRIES = {item.split(':', 1)[0]: item.split(':', 1)[1] for item in (
    'AL:Albania|AD:Andorra|AM:Armenia|AT:Austria|AZ:Azerbaijan|BY:Belarus|'
    'BE:Belgium|BA:Bosnia and Herzegovina|BG:Bulgaria|HR:Croatia|CY:Cyprus|'
    'CZ:Czechia|DK:Denmark|EE:Estonia|FI:Finland|FR:France|GE:Georgia|'
    'DE:Germany|GR:Greece|HU:Hungary|IS:Iceland|IE:Ireland|IT:Italy|'
    'KZ:Kazakhstan|LV:Latvia|LI:Liechtenstein|LT:Lithuania|LU:Luxembourg|'
    'MT:Malta|MD:Moldova|MC:Monaco|ME:Montenegro|NL:Netherlands|'
    'MK:North Macedonia|NO:Norway|PL:Poland|PT:Portugal|RO:Romania|'
    'RU:Russia|SM:San Marino|RS:Serbia|SK:Slovakia|SI:Slovenia|ES:Spain|'
    'SE:Sweden|CH:Switzerland|TR:Türkiye|UA:Ukraine|GB:United Kingdom|VA:Holy See'
).split('|')}
EU_EEA = frozenset('AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE IS LI NO'.split())
SCOPES = ('unknown', 'countries', 'europe', 'eu_eea', 'worldwide')
WORK_MODELS = ('unknown', 'fully_remote', 'remote_with_travel', 'hybrid', 'mixed')
ELIGIBILITY_FIELDS = {'scope','countries','work_model','restrictions','checked_at','sources'}


def eligibility(row):
    """Unknown is not ineligible; never infer countries from legacy signals."""
    return row.get('eligibility', {'scope':'unknown','countries':[], 'work_model':'unknown',
                                   'restrictions':[], 'checked_at':'','sources':[]})


def privacy(value):
    """Apply the original strict sentinels recursively, including URL lists."""
    if isinstance(value, str):
        assert not re.search(r'/home/|/Users/|\[\[|fit_for_pau|manual_status_lock|rejection_reason|@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|gh[pousr]_[A-Za-z0-9]|sk-[A-Za-z0-9]', value), 'Private content or secret-like data'
    elif isinstance(value, dict):
        for key, item in value.items():
            privacy(key)
            privacy(item)
    elif isinstance(value, list):
        for item in value:privacy(item)


def validate_eligibility(e):
    assert isinstance(e, dict) and set(e) == ELIGIBILITY_FIELDS, 'Invalid eligibility fields'
    assert e['scope'] in SCOPES and e['work_model'] in WORK_MODELS
    assert isinstance(e['countries'], list)
    assert all(isinstance(c, str) and c in COUNTRIES for c in e['countries']), 'Use European ISO country codes (GB, not UK)'
    assert len(set(e['countries'])) == len(e['countries'])
    assert isinstance(e['restrictions'], list) and all(isinstance(v, str) and v.strip() for v in e['restrictions'])
    assert isinstance(e['sources'], list) and all(isinstance(v, str) for v in e['sources'])
    assert isinstance(e['checked_at'], str)
    if e['checked_at']:
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', e['checked_at'])
        try:date.fromisoformat(e['checked_at'])
        except ValueError:raise AssertionError('Invalid eligibility date') from None
    for source in e['sources']:url(source)
    assert e['scope'] != 'unknown' or not e['countries'], 'Unknown scope cannot confirm countries'
    assert e['scope'] != 'countries' or e['countries'], 'Country scope requires countries'
    if e['scope'] == 'eu_eea':assert set(e['countries']) <= EU_EEA, 'EU/EEA excludes GB and Switzerland'
    if e['countries'] or e['scope'] in ('europe','eu_eea','worldwide'):
        assert e['checked_at'] and e['sources'], 'Confirmed eligibility requires a date and official public evidence'


def regional_hint(row, country):
    e=eligibility(row)
    return country not in e['countries'] and (e['scope'] in ('europe','worldwide') or (e['scope']=='eu_eea' and country in EU_EEA))
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
        assert set(r) in (FIELDS, FIELDS | {'eligibility'}), (r.get('name'),set(r)^FIELDS)
        privacy(r)
        validate_eligibility(eligibility(r))
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

def eligibility_card(row):
    e=eligibility(row)
    return ['', '## Structured eligibility', '',
            f"- **Scope:** {e['scope']}",
            f"- **Explicit countries:** {', '.join(e['countries']) or 'None verified'}",
            f"- **Work model:** {e['work_model']}",
            f"- **Restrictions:** {'; '.join(e['restrictions']) or 'Not recorded (not a claim of no restrictions)'}",
            f"- **Eligibility checked:** {e['checked_at'] or 'Not verified'}",
            '- **Eligibility sources:** '+(' ; '.join(e['sources']) or 'None verified'), '',
            'Unknown is not ineligible. Historical remote signals are not country eligibility.']


def render_countries(rows):
    directory=ROOT/'countries';directory.mkdir(exist_ok=True)
    def links(items):
        return [f"- [{r['name']}](../companies/{r['id']}.md) — {eligibility(r)['work_model']}" for r in items] or ['None recorded.']
    intro=['# Browse by country', '', '[Back to directory](../README.md)', '',
           'Exact matches require an explicitly verified country code. Regional hints are not country confirmation.',
           'Unknown is not ineligible. Work models and restrictions still require role-level checking.', '',
           '[Country code reference](countrycodes.md) · [Unknown eligibility](unknown.md)', '']
    codes=['# Country codes', '', '[Browse countries](README.md)', '',
           'European ISO 3166-1 alpha-2 codes used by this directory (including transcontinental states).',
           'Use GB, not UK. EU is a region, not a country. EU/EEA excludes GB and CH.',
           'No unassigned pseudo-codes: Kosovo is not assigned an ISO 3166-1 alpha-2 code.', '']
    for code,name in sorted(COUNTRIES.items()):
        exact=[r for r in rows if code in eligibility(r)['countries']]
        hints=[r for r in rows if regional_hint(r,code)]
        intro.append(f'- [{name} ({code})]({code}.md) — {len(exact)} exact; {len(hints)} regional hints')
        codes.append(f'- {code}: {name}')
        content=[f'# {name} ({code})', '', '[Browse countries](README.md)', '',
                 'Unknown is not ineligible. These are research leads, not current vacancy guarantees.', '',
                 '## Exact country matches', '', *links(exact), '',
                 '## Regional hints — not confirmed country eligibility', '',
                 'Only structured Europe, EU/EEA or worldwide scope; historical signals are not used.', '', *links(hints), '']
        (directory/f'{code}.md').write_text('\n'.join(content))
    unknown=[r for r in rows if eligibility(r)['scope']=='unknown']
    (directory/'unknown.md').write_text('\n'.join(['# Unknown eligibility', '', '[Browse countries](README.md)', '',
        'Unknown is not ineligible. No country eligibility has been confirmed; legacy signals never supply countries.', '', *links(unknown), '']))
    (directory/'README.md').write_text('\n'.join(intro)+'\n')
    (directory/'countrycodes.md').write_text('\n'.join(codes)+'\n')


def main():
    rows=validate(json.loads((ROOT/'data/companies.json').read_text()))
    rows=sorted(rows,key=lambda x:x['name'].casefold())
    counts=Counter(r['remote_signal'] for r in rows)
    lines=['# Remote companies — Europe','',f'A public, source-linked directory of **{len(rows)} companies** for people researching remote-friendly work across Europe.','',
    '**This is a research directory, not a guarantee of current vacancies or eligibility.** Some entries have only historical signals, mixed hybrid policies or country restrictions. Always read the actual vacancy and confirm employment country, office attendance, timezone and contract terms. “Remote” does not mean “work from any country”.','',
    '## Browse','', '- [Browse by country](countries/README.md)', '- [Alphabetical company profiles](companies/README.md)', '- [JSON dataset](data/companies.json)', '- [CSV dataset](data/companies.csv)', '- [Methodology and status definitions](METHODOLOGY.md)', '- [Contribute a correction or company](CONTRIBUTING.md)','',
    '## Historical signals — not country eligibility','', '*These labels summarize historical research signals, not freshly verified company-wide policies.*','']
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
        card += eligibility_card(r)
        if r['verification_note']:card+=['', '## Verification caveat','',r['verification_note']]
        card+=['','## Sources','']+[f'- {s}' for s in r['sources']]+['','Country eligibility, current openings and attendance requirements must be checked for the individual role.','', '[Back to directory](../README.md)','']
        (companydir/(r['id']+'.md')).write_text('\n'.join(card))
    (ROOT/'README.md').write_text('\n'.join(lines)+'\n\n## License\n\nOriginal directory data and editorial descriptions: [CC BY 4.0](LICENSE-DATA.md). Build/validation code: [MIT](LICENSE). Company names, trademarks and linked material remain their respective owners’ property.\n')
    (companydir/'README.md').write_text('\n'.join(index)+'\n')
    render_countries(rows)
    out=io.StringIO();fields=['id','name','description','category','website','careers_url','remote_signal','remote_note','record_reviewed_at','public_sources_checked_at','verification_note','sources']+['eligibility_'+key for key in sorted(ELIGIBILITY_FIELDS)];w=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');w.writeheader()
    for r in rows:
        record={key:r[key] for key in fields if key in FIELDS}
        record['sources']=' ; '.join(r['sources'])
        record.update({'eligibility_'+key:json.dumps(value,ensure_ascii=False) if isinstance(value,list) else value for key,value in eligibility(r).items()})
        w.writerow(record)
    (ROOT/'data/companies.csv').write_text(out.getvalue())
    for f in ROOT.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',f.read_text()):
            if '://' not in target and not target.startswith('#'):assert (f.parent/target.split('#')[0]).exists(),(f,target)
    expected_cards={r['id']+'.md' for r in rows}
    actual_cards={f.name for f in companydir.glob('*.md') if f.name != 'README.md'}
    assert actual_cards == expected_cards, 'Company card set mismatch: '+json.dumps({
        'missing':sorted(expected_cards-actual_cards),
        'unexpected':sorted(actual_cards-expected_cards)})
    print(json.dumps({'companies':len(rows),'cards':len(actual_cards),'signals':dict(counts),'local_links':'pass','schema':'pass'}))

if __name__=='__main__':main()
