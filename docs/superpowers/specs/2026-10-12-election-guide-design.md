# Election guide: "The $18.9 billion question" (design)

**Date:** 2026-10-12
**Status:** draft for review
**Builds on:** `2026-10-12-follow-the-budget-design.md` (ground rules §4, fact rule §6, visual design §5)
**Mockup:** `docs/superpowers/mockups/vote-walk.html` (open it in a browser; candidate names and quotes are placeholders)

## 1. Goal

Get young Toronto voters to vote on **October 26, 2026** by showing them what council actually decides, in dollars, and what each candidate has published about it. The guide is shared as a LinkedIn post that links to `/vote`.

What makes it different from existing candidate trackers (for example, Build Canada's): every topic starts with the money it controls, taken from the site's checked budget data.

## 2. Scope

**In the first version**
- The mayor's race (all candidates).
- City council, Scarborough wards 20–25 (about 53 candidates).
- Policies come **only from material the candidates have already published**: campaign site, platform document, official social accounts.

**Later (the design must allow these without rework)**
- The other 19 wards, added by writing data files only.
- TDSB trustees (separate ward boundaries), then the other school boards.
- A questionnaire sent to candidates.

**Not included:** endorsements, rankings, polls, scores, "who should you vote for" quizzes, and candidate photos.

## 3. Ground rules (from the main spec §4, applied to candidates)

1. **Only their words and the public record.** We don't write summaries, labels ("progressive", "tough on crime") or any characterization of a candidate.
2. **Same treatment for everyone.** Every candidate gets the same fields, the same topics and the same limits. Candidates are listed **alphabetically by last name, as on the ballot**, and never reordered.
3. **No colour for candidates.** Colours belong to topics only. Blue, orange and green read as party colours in Ontario, so a candidate's plaque is always white with a neutral border.
4. **No "vote for/against" messaging.** The guide encourages people to vote and links to the City's official voter information. Never pay to promote the post. Before launch, confirm with the City Clerk's elections office that a free, equal-treatment guide is not third-party advertising.
5. **Corrections.** A visible "Something wrong?" link goes to a project email address, and fixes go into the dated log on `/sources`.

## 4. The experience

### 4.1 `/vote`: the walk (main page, LinkedIn landing)

A scrolling "museum walk" in the site's newspaper style, reusing the pattern from the home page walk.

1. **Entrance.** The headline is "The $18.9 billion question", with the election date and one paragraph on why council matters. Below it is **the ticket**:
   - Choose the race: **My ward** or **Mayor**.
   - Choose a ward: buttons for 20–25, or tap a ward on the map, or enter a postal code (reusing `RepLookup`).
   - Readers outside Scarborough are offered the mayor's race and a link to the City's official candidate list.
2. **The map** stays pinned beside the rooms (above them on phones). It uses the real ward boundaries from `toronto-wards-geojson`, smoothed, with rounded edges. Your ward is filled with the current room's colour as a slowly moving gradient. Other wards get a light tint of that colour. The route draws itself up to the current stop, and a small dot travels along it. The current stop pulses, and stops already passed turn dark.
3. **Five rooms**, walked in this order, each with one colour, one Scarborough place and one budget number:

| # | Room (reader-facing title) | Place | Colour | Money shown (fact id) |
|---|---|---|---|---|
| 1 | Your tax bill | Home | orange `#d9822b` | `toronto.property-tax.2026.avg-bill`, `…increase` |
| 2 | Getting around | Kennedy Station | blue `#2f5d9b` | `toronto.ttc.2026.gross`, `…net` |
| 3 | Rent and housing | Scarborough Centre | green `#4a8c5c` | `toronto.shelter.2026.gross` |
| 4 | What gets built here | 4610 Finch Ave E | teal `#3f7f74` | `scarborough.capital.finch-ltc` (ward view: that ward's top projects) |
| 5 | Safety | 43 Division | purple `#7a5c99` | `toronto.police.2026.gross` |

   Each room contains:
   - The money, shown as a big number. It must come from a `<Fact>`; the existing content check bans hand-typed figures.
   - A **"Who decides"** line.
   - **The wall of plaques.** There is one plaque per candidate who has published something on this topic, in ballot order, each showing their exact quote, a source link and "checked on [date]". Incumbents also get a "holds this seat" tag and a link to their recorded 2026 budget votes.
   - Everyone with nothing on this topic is listed in one line: "Nothing published on this yet: …".
4. **Exit.** "Everyone running in [your ward]", plus links to the race page, the mayor's race and the City's where-and-when-to-vote page. A blue, orange and green ribbon closes the page.

**Motion:** room colours fade in, plaques slide in one after another, the route draws itself, and the ward gradient drifts. Under `prefers-reduced-motion`, all of this is static and the travelling dot is hidden.

### 4.2 Race pages: `/vote/mayor`, `/vote/ward-20` … `/vote/ward-25`

These show full candidate cards in ballot order. Each card has:
- Name and "holds this seat" (if true).
- Past elected offices, from the public record, with a source.
- Official campaign site.
- The five topics, each with a quote or "Nothing published on this yet".
- For incumbents, their recorded votes, from `people.yaml`.

A **"Compare one topic"** switch shows a single topic for every candidate.

Ward pages open with the ward's money: population and 10-year capital spending (from `wards.json`). These pages are what the walk's "all candidates ›" links open, and they work on their own without the walk.

### 4.3 Header

The header gains a navigation row: **2026 Election · Scarborough · Toronto · Ontario**. Until after the election, the Election link is first and highlighted. For now, "Scarborough", "Toronto" and "Ontario" link to the existing walk and explorer. The page-per-place restructure is a separate, later project.

## 5. Data

### 5.1 Files

`data/candidates/<race>.yaml`, one file per race (`mayor`, `ward-20` … `ward-25`):

```yaml
race: ward-21
office: City Councillor, Ward 21 Scarborough Centre
official_list:            # where the candidate list came from
  url: https://www.toronto.ca/...   # City Clerk's certified candidate list
  checked: 2026-10-13
candidates:
  - id: ward-21.lastname-firstname
    ballot_name: "LASTNAME, Firstname"   # exactly as on the official list
    incumbent: false
    website: https://...                 # official campaign site, or null
    offices:                             # past elected offices, public record only
      - { title: "...", years: "2018–2022", source: { url: "...", title: "..." } }
    topics:
      tax:      [ ]                      # 0–2 quotes each
      transit:  [ ]
      housing:  [ ]
      build:    [ ]
      safety:   [ ]
```

Each quote:

```yaml
- text: "Exact words, max 60 words, no edits except […] for cuts"
  url: https://...          # the page where they said it
  archive: https://web.archive.org/web/...   # saved copy
  published: 2026-09-30     # if the page shows a date, else null
  retrieved: 2026-10-14
  status: draft | checked   # only "checked" is ever shown
  checked_by: ...           # who confirmed it against the source
  checked_on: 2026-10-15
```

`id` matches the `people.yaml` id for incumbents, so their votes link up.

### 5.2 Topic definitions

`data/candidates/topics.yaml` defines the five topics: id, reader title, colour, fact ids, "who decides" text, and **what counts as on-topic** (for example, transit includes TTC fares, service, subways/LRT/busways and road safety for transit users). This keeps the decisions about which quote goes where consistent across all candidates.

### 5.3 Candidate list pipeline

`pipeline/candidates.py`:
1. Fetches the City Clerk's certified candidate list. It is a new entry in `fetch.py`, recorded in `sources.json`.
2. Writes `data/clean/candidates-official.json`.
3. Creates any missing candidate entries in the YAML files with empty topics. It never overwrites existing quotes.

It runs again before launch and in the final week. Withdrawals are removed and logged on `/sources`.

## 6. Checks (fail the build)

Added to `site/scripts/check-content.mjs` (or a sibling `check-candidates.mjs`). Each race file must satisfy:
- Its candidates exactly match `candidates-official.json`: none missing, none extra, names identical.
- Every candidate has every topic key and the same field set.
- At most **2 quotes per topic**, each **at most 60 words**.
- Every quote has `url`, `archive`, `retrieved` and `status`. `checked` quotes also have `checked_by` and `checked_on`.
- Every `offices` entry has a source.
- **A race page is only built if every quote in that race is `checked`.** Until then, the race shows "This race is being reviewed" and lists names only. A draft is never shown, and never shown as "nothing published".
- Room numbers use `<Fact>`; the existing rule still applies.
- Plaque and card components take no colour from candidate data. This is enforced by the component API, which has no colour prop.

## 7. Review tool (dev only)

`/review` only exists in `vite dev` and is excluded from the static build. It lists every draft quote with:
- the source link and archive link opened side by side,
- **Approve** (sets `status: checked`, `checked_by`, `checked_on`),
- **Reject** (removes the quote and records why in a local review log).

It writes back to the YAML through a dev-only endpoint. The aim is to make roughly 25–35 hours of checking as fast as possible.

## 8. Roles

- **Claude:** finds sources, drafts quotes, saves archives, builds the pages, checks and review tool.
- **The site owner:** checks every quote in `/review`, creates the corrections email, calls the City Clerk's office about advertising rules, posts on LinkedIn.

## 9. Timeline (election Mon Oct 26)

| Dates | Work |
|---|---|
| Oct 13–14 | Candidate pipeline, data files, checks; walk and race pages with placeholder data |
| Oct 13–17 | Gather sources and draft quotes, mayor's race first, then wards |
| Oct 15–20 | Review in `/review` (about 25–35 h); fix issues |
| Oct 19 | Hosting live; Clerk's office answer in hand; corrections email live |
| Oct 20 | Soft launch and LinkedIn post (advance voting dates per the City) |
| Oct 23 | Re-check candidate list and changed websites |
| Oct 26 | Election day |

If review falls behind, races launch one at a time as each passes the "all checked" rule. The mayor's race goes first because it applies to everyone.

## 10. Testing

- Pipeline unit tests: parsing the official list; merging into YAML never overwrites quotes.
- Check-script tests with fixture files: missing topic, 61-word quote, extra candidate, draft quote in a live race. Each must fail.
- Playwright:
  - `/vote` renders at 390px and 1280px with no horizontal scroll.
  - The ticket switches ward and race.
  - Rooms activate on scroll.
  - Reduced motion is respected.
  - Race pages list candidates in ballot order.
  - `/review` is absent from the static build.
