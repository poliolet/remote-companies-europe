# Methodology

## Scope

This directory brings together public company identities and links from a remote-work research list. It includes remote companies, role-dependent remote employers, mixed/hybrid employers and leads that still need verification. Inclusion is not an endorsement or a statement that a company is currently hiring in Spain.

The initial catalog preserves the complete deduplicated company list. Personal research annotations, candidate histories, compensation negotiations, contacts and private material are excluded. Company descriptions are short original editorial summaries grounded in linked public sources.

## Dates and evidence

- `record_reviewed_at`: historical research-record date, not a guarantee that the company policy was reverified on publication day.
- `public_sources_checked_at`: date of public-source research for the business description and website. A blocked source is disclosed in the verification caveat. This is not an all-vacancies audit.
- `sources`: public references supporting identity, description or careers information. A reference may become stale after publication.

## Remote-signal labels

- **Spain remote signal:** historical evidence of at least one Spain-compatible remote role, or an entry in a Spain-focused remote-company source. Role-level evidence does not establish all-role eligibility.
- **Europe / EMEA remote signal:** historical European-region remote signal; Spain hiring entity, EOR or contractor eligibility still needs confirmation.
- **Global / distributed signal:** distributed/remote wording without guaranteed acceptance from every country.
- **Hybrid or country-restricted evidence:** reviewed evidence includes office attendance, mixed arrangements or a country restriction. Check current vacancies; this is not a claim that all roles are hybrid or restricted.
- **Needs verification:** evidence is insufficient, unclear or only a research lead.

Remote labels are deliberately conservative and based on historical signals. The main directory is not a list of confirmed currently open jobs. Always verify hiring country, employment/contract route, work authorization, timezone overlap, travel and office requirements for each role.

## Rebuilding

Python 3, standard library only:

```sh
python3 scripts/build.py
```

The public builder reads only `data/companies.json`. It does not access any private source, account, mailbox or local knowledge base. Generated Markdown and CSV are checked for schema, duplicate names/IDs, public URL shape and local links.

## Updates

This is an initial public snapshot. There is no automatic synchronization from private research. Submit corrections through a pull request or issue with public evidence; do not include personal contact details, applicant information or private screenshots.
