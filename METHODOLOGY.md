# Methodology

## Scope

This public directory covers remote-friendly employers across Europe without prioritizing any one country. **New companies must offer genuine remote work in at least one European country or have a credible European remote policy, supported by official public evidence.** Weekly-office hybrid-only employers do not qualify for new inclusion. Role-dependent or mixed employers qualify only when at least one evidenced arrangement meets this remote criterion.

Legacy hybrid entries and research leads are retained with their visible historical labels, unknown eligibility and/or verification caveats; they are **not remote-work guarantees** and do not relax the inclusion rule for new companies. Inclusion is not an endorsement, a live jobs feed or confirmation of country eligibility.

The complete deduplicated initial catalog is preserved. Personal annotations, candidate histories, compensation negotiations, contacts and private material are excluded. Business descriptions are short original editorial summaries grounded in linked public sources.

## Dates and evidence

- `record_reviewed_at`: historical research-record date; not a fresh policy check.
- `public_sources_checked_at`: public-source research date for the description and website; not an all-vacancies audit. Blocked sources are disclosed in verification caveats.
- Legacy `sources`: public references supporting identity, description or careers information; they may become stale.
- `eligibility.checked_at`: actual date the official eligibility evidence was checked, in valid `YYYY-MM-DD` calendar format. A date does not guarantee the policy remains current.
- `eligibility.sources`: official company policy, careers or official ATS URLs supporting the structured claim. Human reviewers must check authority and what the evidence actually says. The builder checks public HTTPS URL shape, not domain ownership or source truth; there is no network validation or inference.

## Structured eligibility

The optional `eligibility` object has exactly six fields:

| Field | Meaning |
| --- | --- |
| `scope` | `unknown`, `countries`, `europe`, `eu_eea`, or `worldwide` |
| `countries` | Explicitly supported European ISO 3166-1 alpha-2 codes, not inferred regional members |
| `work_model` | `unknown`, `fully_remote`, `remote_with_travel`, `hybrid`, or `mixed` |
| `restrictions` | List of public limitations: roles, country, authorization, timezone, attendance, contract route or travel |
| `checked_at` | Calendar date or empty string when not checked |
| `sources` | List of official public HTTPS evidence URLs |

Absent objects default to `unknown`, empty lists and an empty date without changing the source JSON. **Unknown is not ineligible.** Empty restrictions mean “not recorded”, never “unrestricted”. Confirmed countries or any broad scope require a date and official evidence. `countries` scope requires a nonempty list; `unknown` cannot confirm countries. A broad scope can retain a separately verified explicit subset; EU/EEA subsets cannot include nonmembers.

The fixed [country-code reference](countries/countrycodes.md) includes European and transcontinental states plus Cyprus. It uses assigned ISO codes only: `GB`, not `UK`; no `EU` country or unassigned pseudo-code. This is a directory convention, not a geopolitical eligibility claim. EU/EEA is the EU plus Iceland, Liechtenstein and Norway; neither GB nor Switzerland belongs to this group.

`fully_remote` is not permission to work from any country. Planned quarterly on-sites are acceptable as `remote_with_travel`, not `fully_remote`: recording travel frequency and who pays travel costs in `restrictions` is mandatory. If either is not stated by the official source, explicitly record it as unknown and needing confirmation; never imply employer-paid travel. Required weekly office attendance is `hybrid` and cannot qualify a hybrid-only new employer. `mixed` covers differing arrangements among roles. Country-restricted remote roles can still be `fully_remote`; record both the country restriction and work model. A single vacancy does not establish company-wide policy. See [synthetic contribution examples](CONTRIBUTING.md).

## Country browsing and filtering

[Country pages](countries/README.md) separate **exact country matches** (explicit verified code) from **regional hints** (structured Europe, EU/EEA or worldwide scope with no explicit code for that country). Regional wording is never expanded into exact matches. Legacy remote signals do not produce regional hints. The unknown page lists records whose geographic scope is unknown, even if other information is available.

The standard-library CLI emits JSON with separate `matches` and `hints` arrays. Default output contains only explicit country matches; `--include-regionals` enables hints. Optional work-model filtering applies to both arrays. It does not infer from text or historical signals.

```sh
python3 scripts/filter.py --country FR
python3 scripts/filter.py --country FR --work-model fully_remote --include-regionals
python3 scripts/filter.py --country GB --include-regionals
```

`--file path/to/public.json` selects another validated public dataset. GB cannot match an EU/EEA hint. Unknown entries are not silently excluded as ineligible: they remain in the dedicated unknown browsing page, not in country results without evidence.

CSV preserves every existing column and appends `eligibility_` columns for all six fields. List fields (`countries`, `restrictions`, `sources`) are JSON-serialized inside CSV cells; use a CSV parser, then JSON-decode those cells. All company cards display structured eligibility, including unknown defaults.

## Historical remote signals — not eligibility

The legacy values and meanings remain compatible:

- **Spain remote signal:** historical evidence of a Spain-compatible role or Spain-focused directory mention; not all-role eligibility.
- **Europe / EMEA remote signal:** historical regional wording; not confirmation of any specific hiring country.
- **Global / distributed signal:** remote/distributed wording; not guaranteed acceptance from every country.
- **Hybrid or country-restricted evidence:** historical mixed arrangements, office attendance or country restrictions; not a claim that every role is restricted.
- **Needs verification:** unclear or insufficient evidence, or a research lead.

These labels never override structured eligibility or fill in missing countries. Always check the individual role's employment/contract route, work authorization, timezone, travel and office requirements.

## Rebuilding and updates

Python 3, standard library only:

```sh
python3 -m unittest discover -s scripts -v
python3 scripts/build.py
```

The builder reads only `data/companies.json`, with no network, private source, account, mailbox or local knowledge base. It validates strict field allowlists, nested privacy sentinels, duplicate names/IDs, eligibility enums/conflicts, dates, public URL shape and local Markdown links. Tests are synthetic and use isolated temporary directories. There is no automatic synchronization from private research. Submit public evidence through a pull request or the company issue form; never submit personal applicant data.
