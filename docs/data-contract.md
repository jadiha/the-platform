# Data contract

The pipeline (`pipeline/`, Python) writes these files. The site (`site/`, SvelteKit) reads only these. All money is in **$ millions (float)** unless a field says otherwise.

## Fact registry: `data/facts/*.yaml`

The files are split by owner: `toronto.yaml`, `ontario.yaml`, `schools.yaml`, `scarborough.yaml`, `federal.yaml`. Each file is a map from fact ID to a record:

```yaml
ontario.expense.2026-27.total:
  value: 244200          # number (or string for non-numeric facts, e.g. a date)
  unit: $M               # $M | $ | % | people | date | count
  label: "Ontario total spending, 2026-27 plan"
  basis: "consolidated, plan"     # say gross/net and budget/interim/actual where relevant
  primary: {title: "2026 Ontario Budget, Table 3.1", url: "https://budget.ontario.ca/2026/chapter-3.html", locator: "Table 3.1"}
  crosscheck:            # required when status = verified
    - {title: "CBC News", url: "...", date: 2026-03-26, value: 244000, note: "rounded"}
  status: verified       # verified | single | disagree | reported
  note: "optional plain-language caveat shown in the popover"
  as_of: 2026-10-12
```

`disagree` requires at least two entries, across primary and crosscheck, with different values, plus a `note` explaining why they differ.

## People: `data/people.yaml`

```yaml
- id: chow-olivia
  name: Olivia Chow
  role: Mayor of Toronto
  level: city            # city | province | federal | school
  party: null
  ward_or_riding: null
  term: {start: 2023-07-12, end: null}
  on_ballot_2026: true
  official_url: "..."
  decisions:             # public record only
    - {date: 2026-02-10, what: "...", vote: "yes|no|absent|proposed|n/a", item: "2026.BU1.x", source: {title, url}}
  quotes:
    - {date: ..., text: "exact words", context: "...", source: {title, url}}
  as_of: 2026-10-12
```

## Budget trees: `data/clean/budget-<level>-<year>.json`

The levels are `ontario`, `toronto` and `scarborough`. Each file holds one node:

```json
{ "id": "toronto", "name": "City of Toronto", "year": "2026", "basis": "gross, approved budget",
  "gross": 18864.0, "net": 5800.0,
  "source": {"title": "...", "url": "...", "locator": "p. 12"},
  "children": [
    {"id": "toronto.transit", "name": "Transit", "category": "transit",
     "gross": 3028.0, "net": 1481.0,
     "originalLines": ["Toronto Transit Commission - Conventional", "Toronto Transit Commission - Wheel-Trans"],
     "children": [ ... ] }
  ] }
```

- `category` is one of the shared categories: `transit, police-justice, fire-paramedics, housing-shelter, social-services, health, education, parks-rec-culture, infrastructure, government-debt, other`.
- **Invariant:** each node's `gross` equals the sum of its children's `gross`, within 0.5 $M. The pipeline checks this.
- `net` may be `null` where it is not published.

## Trends: `data/clean/trends.json`

```json
{ "ontario": { "health": [{"year": "2021-22", "value": 69600, "kind": "actual", "sourceRef": "ontario-budget-2023"}] },
  "toronto": { ... } }
```

`kind` is one of `actual | interim | plan`.

## Wards: `data/clean/wards.json`

```json
{ "asOf": "...", "capitalPlan": "2026-2035",
  "cityWide": {"capital10yr": 55025.0, "share": 0.873},
  "wards": [ {"ward": 20, "name": "Scarborough Southwest", "scarborough": true,
              "population": 110095, "capital10yr": 109.9, "capital2026": 0.0,
              "perResident10yr": 998.6,
              "topProjects": [{"name": "...", "program": "...", "amount10yr": 66.0, "category": "..."}] } ] }
```

## Sources manifest: `data/sources.json`

```json
[ { "id": "toronto-capital-2026", "title": "...", "url": "...", "fetchedAt": "...", "sha256": "...", "file": "data/raw/..." } ]
```

## Category mappings: `data/mappings/<level>.csv`

Columns: `original_line,category,notes`. Every source line must appear exactly once.
