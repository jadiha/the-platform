# The Platform

**Live: [torontoyourvotecounts.space](https://www.torontoyourvotecounts.space)**

A non-partisan guide to Toronto's municipal election on **Monday, October 26, 2026**, and to where Toronto's and Ontario's public money goes. It's an independent community project, not affiliated with any government, party or candidate.

## What's on the site

- **The election ride** (`/vote/`, the front page). A streetcar trip through the race, one stop at a time:
  1. **Whose job is it?** A quiz: does the City, the Province or the federal government decide it?
  2. **City Hall.** What the mayor and council decide: your property tax bill, how the City's biggest budgets are split, and TTC fares.
  3. **Meet the candidates.** Every mayoral candidate with a campaign website, as a tap-through card: who they are, what they stand for, their promises with numbers, and their links. You can pin up to 3 to compare.
  4. **Also on your ballot.** The mayoral candidates who didn't list a website.
  5. **Your ward.** Councillor and school trustee candidates on a ward map.
  6. **Before you vote.** Who can vote, what ID to bring, and where to vote.
- **Every candidate for mayor** (`/vote/mayor/`). The full ballot in ballot order on one page.
- **Explore the budget** (`/explore/budget/`). Toronto's and Ontario's budgets, from the big categories down to programs.
- **A walk through Scarborough** (`/walk/`). How City and provincial money is spent in one part of the city.
- **People** (`/people/`), **Glossary** (`/glossary/`) and **Sources** (`/sources/`). Who decides, plain-language budget terms, and every dataset behind the site.

## How we keep it accurate

- **Every number has a source.** Figures live in a fact registry (`data/facts/*.yaml`) with a primary source, a page or table locator, and a status (`verified`, `single`, `disagree` or `reported`). On the site, each number can be tapped to show its proof.
- **No numbers typed by hand.** The build fails if story copy contains a dollar or percent figure that isn't drawn from the registry, or if a fact is missing its source.
- **Candidates in their own words.** Quotes are copied word for word from the candidate's own campaign site, link to the exact sentence, and have a saved copy. Each one is checked by a person before it goes live. We don't use news reports or opponents' claims, and we don't predict what a promise would do.
- **Official lists only.** Candidate names and ballot order come from the City Clerk's certified list.

Spotted a mistake? Use the corrections link on the [Sources](https://www.torontoyourvotecounts.space/sources/#corrections) page.

## Repo layout

| Path | What it is |
| --- | --- |
| `site/` | The website (SvelteKit, built as a static site) |
| `data/facts/` | The fact registry: every number the site shows, with its source |
| `data/candidates/` | Mayoral candidate profiles, promises and the "Whose job is it?" questions |
| `data/clean/` | Pipeline output the site reads: budget trees, trends, wards, the official candidate list |
| `data/raw/`, `data/interim/` | Downloaded source files and working files (not deployed) |
| `pipeline/` | Python scripts that download the sources and build `data/clean/` |
| `tests/` | Pipeline tests |
| `docs/data-contract.md` | The exact shape of every file the pipeline writes and the site reads |
| `research/` | Working notes, not site copy |

## Running it locally

You need Node 20+ for the site. The data pipeline also needs Python 3.11+ and [uv](https://docs.astral.sh/uv/).

**The site:**

```sh
cd site
npm install
npm run dev            # http://localhost:5173
npm run check          # type check
npm run build          # content checks, then a static build in site/build/
```

**The data pipeline** (only needed to refresh data; its output is committed):

```sh
uv run python -m pipeline.fetch          # download sources into data/raw/ (--force to refresh)
uv run python -m pipeline.build          # build data/clean/ and people.yaml, then run checks
uv run python -m pipeline.candidates     # rebuild the official candidate list from its snapshot
uv run pytest                            # tests
```

**Reviewing candidate content:** new promises and profiles start as `status: draft`. In `npm run dev`, each draft card shows an approve button. Open every "see it" link, check the words against the candidate's site, then approve. That flips the item to `checked`. The approve button only exists in dev and never ships.

## Deploying

The site is hosted on Vercel and is connected to this repo:

- A push to `main` deploys to production.
- Pushes to other branches get preview URLs.

Build settings are in `vercel.json`, and `.vercelignore` keeps the pipeline and raw data out of the upload.
