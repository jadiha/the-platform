# Follow the Budget: Design Spec

**Date:** 2026-10-12
**Status:** Draft, awaiting review

## 1. Purpose

A public, interactive website that shows young people and community members in Scarborough where government money goes, and who decides. It starts in Scarborough and zooms out to the City of Toronto, then the Province of Ontario.

The site is written for someone who knows nothing about budgets. Every number has to hold up to scrutiny.

**Not in scope for v1:** following money to companies (contracts, lobbyists), council voting records, and deep history (more than about 5 years). The open datasets for these exist (TOBids awarded contracts, lobbyist registry, voting record), but they belong to a later project.

## 2. Audience and tone

- Youth and community members in Scarborough. Assume no prior knowledge.
- Shared publicly, including on social media and at community meetings.
- Tone: calm and credible like a newspaper, with bold headline numbers. Factual, not partisan. The facts should do the persuading.

## 3. Site structure

| Route | What it is | Phase |
|---|---|---|
| `/` | Scroll story, a "memory palace walk" through Scarborough (see §4) | 1 |
| `/explore/budget` | Zoomable treemap: Ontario → Toronto → category → line item | 1 |
| `/explore/map` | Map of capital projects and schools, with wards shaded by $ per resident | 2 |
| `/glossary` | Every jargon term, explained in plain language | 1 |
| `/sources` | Every dataset, the date it was pulled, how categories were mapped, and known gaps | 1 |

## 4. The front page: memory palace walk

A scrollytelling layout. A schematic map of Scarborough stays pinned on one side while the story scrolls past on the other. A route connects real places, and each place teaches one budget idea. The place itself is the memory hook. At the end, the map zooms out to Toronto, then Ontario.

| Stop | Place | Idea it teaches | Main chart |
|---|---|---|---|
| 1 | Home | Property tax: where each $100 goes | Horizontal bars, city spending share |
| 2 | Kennedy Station | TTC is the biggest single city cost; capital vs. operating; Scarborough Busway (opened 2026-09-30), Scarborough Subway Extension | TTC funding sources; project status timeline |
| 3 | Your school | **The city does not fund schools; the Province does.** TDSB under provincial supervision | Funding by source; repair backlog (Phase 2: per school) |
| 4 | Rec centre / long-term care home | Ward-level capital spending; the "fair share" question, answered honestly (see §6.4) | Per-resident ward bars, with the City Wide caveat shown visually |
| 5 | City Hall | Who decides: council, mayor, the budget calendar; Eglinton East LRT funding fight | Toronto budget by category |
| 6 | Queen's Park | Ontario budget by sector; education and health | Ontario spending by sector |
| 7 | What changed | 5-year trends: biggest increases and cuts at each level | Small multiples, one line chart per category |
| 8 | Who represents you | Enter a postal code to get your councillor, MPP, MP and school trustee, plus an election banner | Representative cards |

### Beginner features (on every stop)

- **Jargon popups.** Dotted-underline terms open a one-line plain-English meaning, ideally with an everyday comparison ("operating budget = rent and groceries; capital = buying a car").
- **"Who decides this?" line.** Which government controls this money, and when it votes.
- **"Wait, what about…" callouts.** These head off common misunderstandings, such as "the city doesn't fund schools".
- **Verification badge** on every number (see §6).

## 5. Visual design

- **Feel:** a white newspaper data feature (warm off-white `#fdfcf9`), with a serif for headlines and body (Newsreader) and a clean sans for labels and charts (Libre Franklin).
- **Palette:** blue `#2f5d9b`, orange `#d9822b`, green `#4a8c5c`, neutral grey `#c9c5bc`, ink `#121212`. Colour carries meaning only. Each category keeps the same colour across every chart: blue = transit, orange = education, green = housing and community, grey = everything else. The final category-to-colour table is fixed during implementation and checked for colour-blind safety.
- **Motion:** smooth bar growth, map zooms, and stops lighting up as you scroll. No glows or gradients, and nothing that looks like a template. Respect `prefers-reduced-motion`.
- **Mobile first.** On phones the map pins to the top and the text scrolls beneath it. Many visitors will arrive from social media on a phone.
- The approved mockup is at `.superpowers/brainstorm/*/content/newspaper-walk.html`.

## 6. Data and fact-checking

### 6.1 The fact rule

1. Every number comes from an **official primary source**: a government budget document, an Open Data file, Public Accounts, or Metrolinx/TTC. News is never the source of a number.
2. Every **headline number** is cross-checked against at least one independent source: FAO Ontario, the City Auditor General, CBC, Global, CP24, the Star, or The Trillium.
3. Each number gets a status:
   - **✓ Verified:** primary source plus an independent source that agrees.
   - **◌ Single source:** primary source only.
   - **⚠ Sources disagree:** both values are shown, with an explanation.
   - **Reported:** not confirmed by an official source, for example the SSE "2033" opening date or the "$5.5B" cost. Shown only with this label, never as fact.
4. Every number states whether it is **budget or actual** and **gross or net**. In charts, the default is **gross**, labelled "total cost", with net shown as "paid by the city".

### 6.2 Fact registry (single source of truth for numbers)

All prose numbers live in `data/facts.yaml`, one record per fact:

```yaml
toronto.operating.2026.gross:
  value: 18864         # $ millions
  unit: $M
  basis: gross, approved budget
  primary: {title: "2026 City of Toronto Budget Summary", url: "...", page: 12}
  crosscheck: [{title: "CBC News, 2026-02-10", url: "...", value: 18900}]
  status: verified
  as_of: 2026-10-12
```

The front end **never hard-codes a number in prose**. Text references a fact ID, for example `<Fact id="toronto.operating.2026.gross" />`, which renders the number together with its badge and source popover. Chart data comes from the pipeline outputs, not from this registry.

### 6.3 Sources (verified to exist, 2026-10-12)

**City of Toronto / Scarborough**

- *Capital Budget & Plan By Ward* (Open Data, XLSX, $000s). The 2019–2035 files use the 25-ward model, which gives 8 comparable years. Row sum = $63.06B, matching the official $63.1B.
- *Operating Budget Program Summary* (Open Data, whole dollars, revenues negative). Covers up to 2025 only. It does **not** reconcile to the headline totals, so it is used only for drill-down shares.
- *2026 Budget Summary* PDF (292 pp). The source for 2026 operating headline figures.
- *Ward Profiles* (2021 Census custom tabulation). Scarborough wards 20–25 have a population of 623,610.
- *City Wards* GeoJSON. Ward ID is in `AREA_SHORT_CODE` (zero-padded).
- *Toronto Police budget* (Open Data, 2020–2026).
- TTC / Metrolinx project pages, for project status.

**Ontario**

- *2026 Ontario Budget*, chapter 3 (HTML tables only, scraped).
  - Table 3.1: totals. 2026-27 plan is $244.2B total expense and a $13.8B deficit.
  - Table 3.7: by sector. Health $101.2B, Education $40.8B, Postsecondary $14.0B.
  - Table 3.10: by ministry.
  - Table 3.12: the restated 10-year series, used for the 5-year totals.
- *Public Accounts 2025-26* (released 2026-09-24): actuals, with a 2025-26 deficit of $13.0B. Its ministry CSV on data.ontario.ca is in whole dollars and non-consolidated.
- *First Quarter Finances 2026-27*: the deficit is unchanged.
- Cross-checks:
  - FAO's *2026 Budget Note*, *Summer 2026 EBO*, and *Ministry of Education Spending Plan Review* (2026-09-23).
  - CBC / CP / Globe and Mail confirm $244.2B and $13.8B.

**Schools**

- *Core Education Funding projections 2026-27* (ministry PDF). TDSB gets $3.375B, a 1.1% decrease; TCDSB gets $1.269B. Note that TDSB's own document says $3,377.7M; never mix the two sources.
- *TDSB 2026-27 Budget*: revenue $3,594.2M, expenses $3,609.2M, deficit $15.0M.
- *School board financial reports* (EFIS CSV, data.ontario.ca). Wide format; read it using the Cell Name Reference Guide.
- *School Information and Student Demographics* (lat/lng, 2024-25 file). Schools are assigned to Scarborough by mapping their coordinates against the ward boundaries, not by the "City" field, which is unreliable.
- *Ontario school board oversight page*: TDSB has been under a supervisor since 2025-06-27.
- Facility condition:
  - TDSB per-school FCI comes from scraping tdsb.on.ca, data as of January 2025 (Phase 2).
  - FAO's *School Boards Capital 2024*: a $6.5B backlog province-wide.

**Ontario and schools traps**

- **Education sector vs. ministry.** The sector figure ($40.8B) excludes the teachers' pension; the ministry figure ($42.5B) includes it. Never put both in one chart.
- **Budget, Estimates and Public Accounts are three different bases.** Each chart uses one basis and says which.
- **Restatements.** Each new document revises earlier years. A 5-year chart uses Table 3.12 for totals, and the latest document for each year's sector figures. Each point is labelled Actual, Interim or Plan. COVID-era funding appears as its own line, with a footnote.
- **FAO numbers are forecasts.** They are used for context, not as a cross-check of actuals.

**Open questions (must be resolved from primary text before publishing)**

- TCDSB's 2026-27 deficit: $39.5M in news reports vs. $44.3M in EFIS.
- Which law capped trustees at 12. One research pass found Bill 33 (2025), another Bill 101 (Royal Assent 2026-05-07). Read the bill text on ola.org.
- Scarborough school closures: none verified.
- Which named capital projects are actually in Scarborough: to be matched by coordinates.

**Representatives**

- Represent API (Open North). Used **only** to map a postal code or location to a ward or riding. Its names are stale.
- The names themselves come from official lists: ourcommons.ca (XML), ola.org, and toronto.ca members of council.
- Edge cases to handle: a vacant seat (Scarborough North MP, vacant since 2026-08-15), and postal codes that straddle two ridings (show both).

**Federal transfers (Phase 1 callout only):** Build Communities Strong Fund (formerly the Canada Community-Building Fund), $183M to the City and TTC in 2025-26; Housing Accelerator Fund (up to $471.1M, cut by $10M in Jan 2026); federal share of the SSE, about $2.26B.

### 6.4 Known traps (must be handled visibly, not just noted in a footnote)

- **City Wide capital.** About 87% of capital dollars are coded "CW", not tied to any ward. Only about $1.14B over 10 years is tagged to Scarborough wards, and about $422M of that is one LTC home (4610 Finch Ave E). The fair-share chart must show the untraceable portion, and must not imply that Scarborough's total is just its ward-tagged amount.
- **Gross vs. net.** Example: Children's Services is $1.58B gross but $0.10B net.
- **Police $1,708M vs. $1,704.3M.** Two figures appear in the same document. Use the service page figure and show a ⚠ explanation.
- **Ministry reorganizations** break 5-year Ontario comparisons. Map them through the shared categories and document each mapping.
- **Election timing.** The Toronto municipal election is on 2026-10-26, and the new term starts 2026-11-15. Councillor and trustee data carries an "as of" date, an election banner, and a post-election update task.

### 6.5 Shared categories

Every government's line items are mapped to one shared set: Transit, Police & Justice, Fire & Paramedics, Housing & Shelter, Social Services, Health, Education, Parks/Rec/Culture, Infrastructure (roads, water), Government & Debt, Other.

The mapping is a reviewed CSV (`data/mappings/*.csv`) published on `/sources`. Hovering a treemap tile shows the original line names.

## 7. Architecture

```
pipeline/ (Python)                    site/ (SvelteKit, static)     
  fetch/   → data/raw/  (as published, + fetched_at)
  build/   → data/clean/*.json  ──►    story, treemap, map read only clean JSON
  checks/  → fails build on mismatch   facts.yaml → <Fact> component
```

- **Pipeline:** Python (pandas, openpyxl, pdfplumber). It is re-run each year, or after an election.
  - `fetch` stores the raw files unchanged, plus a manifest (URL, fetched_at, sha256).
  - `build` normalizes the data into a budget tree: `{id, name, category, level, year, gross, net, perResident, sourceRef, children}`.
- **Site:** SvelteKit with static adapter, D3 (scales, treemap, transitions), Scrollama (scroll triggers), and MapLibre in Phase 2. It deploys as plain files to GitHub Pages or Netlify. There is no backend.
- **Represent API** is called from the browser at runtime (free, 60 requests/min). The official name lists are baked into the build.
- The repository is public, so anyone can audit it.

## 8. Testing and validation

- **Reconciliation checks (pipeline):** for each level and year, the sum of the clean tree must equal the official published total, within a stated tolerance ($1M for city figures in $000s, 0.1% otherwise). Otherwise the build fails.
- **Fact registry lint:** fails if any fact is missing a primary source, URL, basis or as_of date, or if a `verified` fact has no cross-check.
- **Prose lint:** fails if a digit-heavy number appears in story copy outside a `<Fact>` component.
- **Category mapping check:** every source line is mapped exactly once, with no line left over.
- **Playwright smoke tests:** every story stop renders on mobile and desktop widths; the treemap drills in and back out; the postal-code lookup handles a vacant seat and a riding split; reduced-motion mode works.
- **Human review:** before launch, a second person spot-checks 10 random numbers against their sources.

## 9. Phasing

**Phase 1:** stops 1, 2, 5, 6, 7 and 8 complete; stops 3 and 4 with headline data; the treemap, glossary and sources page.

- Recommended target: a soft launch **before the 2026-10-26 municipal election**, with at least stops 1, 2, 4, 5 and 8 live, because that is when people are most interested.
- If the deadline means rushing past the fact rule, launch after the election instead. Accuracy comes before timing.

**Phase 2:** the map tool, per-school data (repair backlog, new builds, closures), detailed Scarborough project pages, and a post-election update.

**Later (separate spec):** follow the money (contracts, lobbyists), council voting records.
