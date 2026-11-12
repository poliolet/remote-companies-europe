# Contributing

Corrections, clearer country restrictions and remote-friendly employers across Europe are welcome. No country has priority.

**New companies must offer genuine remote work in at least one European country or have a credible European remote policy, supported by official public evidence.** Weekly-office hybrid-only employers do not qualify. A mixed or role-dependent employer needs at least one evidenced arrangement meeting this remote criterion. Legacy hybrid entries and research leads remain visibly labeled with historical signals and verification caveats, not remote-work guarantees; their retention is not an exception for new additions. See [methodology](METHODOLOGY.md).

1. Link the official company homepage and stable careers page or official ATS board, not an expiring vacancy when a general board exists.
2. Add a short original factual business description. Do not paste marketing copy or other directories' descriptions.
3. Supply official public evidence and the date you actually checked it. A directory, search snippet or historical remote signal does not confirm country eligibility. A role-specific source supports only that role's constraints; disclose that limitation.
4. Record countries only when the official policy or role explicitly accepts them. Never expand “Europe”, “EMEA”, “EU” or “worldwide” into invented country lists. Use `GB`, not `UK`; `EU` is not a country code. See [country codes](countries/countrycodes.md).
5. Preserve the existing fields. An optional `eligibility` object must contain exactly `scope`, `countries`, `work_model`, `restrictions`, `checked_at`, `sources`. If absent, the builder displays unknown; do not add guessed eligibility to legacy records.
6. Never include private contacts, emails, applicant histories, negotiations, internal documents, private screenshots, authentication links or query strings. The strict privacy allowlist/scanner also applies inside eligibility lists and objects.
7. Edit `data/companies.json`, run the commands below, and include generated CSV, profiles, country pages and README in the pull request. Do not delete an employer solely because one role expired; update its caveat.

## Eligibility examples — synthetic, not employer claims

A fictional official vacancy explicitly accepting France, with quarterly meetups:

```json
{
  "scope": "countries",
  "countries": ["FR"],
  "work_model": "remote_with_travel",
  "restrictions": ["Synthetic example: France-only role; mandatory quarterly in-person meetup; travel cost payer and location unknown, confirm before applying"],
  "checked_at": "2026-11-02",
  "sources": ["https://example.org/careers"]
}
```

Planned quarterly on-sites are acceptable as `remote_with_travel`, not weekly hybrid attendance. Recording travel frequency and who pays travel costs in `restrictions` is mandatory; explicitly mark missing source details as unknown and needing confirmation, never as employer-paid. Weekly required office attendance is `hybrid` even when a vacancy is advertised as remote, and a hybrid-only employer cannot qualify as a new addition. `fully_remote` means the cited arrangement has no mandatory recurring office/travel requirement; it does **not** mean unrestricted geography. Use `mixed` for differing role arrangements, and put role/country limitations in `restrictions`.

For a synthetic regional policy saying EU/EEA without enumerating countries, use `scope: "eu_eea"`, `countries: []`, and dated official evidence. This produces regional hints only, including France but excluding GB and CH. `europe` and `worldwide` also remain hints until a country is explicitly confirmed. Do not infer employment entities, EOR coverage, work authorization or visa sponsorship.

When no reliable eligibility evidence exists, omit the object or use:

```json
{"scope":"unknown","countries":[],"work_model":"unknown","restrictions":[],"checked_at":"","sources":[]}
```

Country-scoped eligibility requires at least one supported European ISO 3166-1 alpha-2 code. Any confirmed country or broad regional scope requires a real calendar date and one or more official HTTPS public sources. Source ownership/authority is reviewed by humans; URL validation alone cannot establish that a source is official.

```sh
python3 -m unittest discover -s scripts -v
python3 scripts/build.py
python3 scripts/filter.py --country FR --work-model fully_remote
python3 scripts/filter.py --country FR --include-regionals
```

Tests use synthetic fixtures only; never invent evidence for a real company. Unknown is not ineligible. Review claims and their limitations before publishing.
