# Election guide: build plan

**Spec:** `docs/superpowers/specs/2026-10-12-election-guide-design.md`
**Mockup:** `docs/superpowers/mockups/vote-walk.html`
**Branch:** `election-guide`
**Deadline:** LinkedIn post around **Oct 20**; election **Mon Oct 26**.

Each task lists **what you'll learn**, so you can follow along. Tasks are in build order. A task is finished when its "Done when" line is true and committed.

---

## Day 1 (Oct 13–14): data first

### Task 1: Traffic fact
- **Files:**
  - `data/facts/toronto.yaml`: add `toronto.transportation.2026.gross` (516.0, Appendix 1.1.2, p. 264).
  - `pipeline/checks.py`: derive the value from `budget-toronto-2026.json`.
- **Learn:** how every number on the site is tied to a source and re-checked automatically.
- **Done when:** `uv run python -m pipeline.checks` passes with 16 facts.

### Task 2: The official candidate list
- **Files:**
  - `pipeline/fetch.py` and `data/sources.json`: new source `toronto-candidates-2026`, the City Clerk's list at https://www.toronto.ca/city-government/elections/candidate-list/.
  - `pipeline/candidates.py`: new.
  - `tests/test_pipeline.py`.
- **Steps:**
  1. Fetch the page and look at its format, whether it's an HTML table, CSV or JSON. Write the parser for what is actually there.
  2. Write `data/clean/candidates-official.json` with each race, its ballot names in ballot order, and any withdrawn flag. Chris Alexander withdrew but stays on the ballot, so he is listed with a note.
  3. Create or merge `data/candidates/<race>.yaml` for `mayor` and `ward-20` to `ward-25`. Add new people with empty topics, and **never touch existing quotes**.
  4. Add `candidates` to `pipeline/build.py`.
- **Tests:** parsing a saved copy of the page; a merge that keeps existing quotes; a removed candidate that is reported, not silently deleted.
- **Learn:** fetching and parsing real-world data, and why a pipeline must be safe to re-run.
- **Done when:** the 7 race files exist with every official candidate, and the tests pass.

### Task 3: Topics and promises files
- **Files:**
  - `data/candidates/topics.yaml`: the 5 rooms, each with its title, colour, place, fact ids, "who decides" text and **what counts as on-topic**. Getting around includes roads and traffic.
  - `data/candidates/promises.yaml`: empty list.
- **Done when:** both files load in Python and Node.

### Task 4: Site types and loaders
- **Files:**
  - `site/src/lib/types.ts`: `Race`, `Candidate`, `Quote`, `Topic`, `Promise`.
  - `site/src/lib/server/data.ts`: `loadRaces()`, `loadTopics()`, `loadPromises()`. These return only `checked` quotes to pages and never drafts. Drafts are only visible through the review tool.
- **Learn:** keeping "what's stored" separate from "what's shown", which is the core of the fairness rule.
- **Done when:** `npm run check` has 0 errors.

### Task 5: Fairness checks
- **Files:**
  - `site/scripts/check-candidates.mjs`: new, run from the `build` script.
  - `site/scripts/fixtures/`: bad-data examples.
- **Checks** (spec §6):
  - Candidates match the official list exactly.
  - Every candidate has the same fields and all 5 topics.
  - At most 2 quotes per topic, and at most 60 words per quote.
  - Every quote has `url`, `archive`, `retrieved` and `status`; checked quotes also have `checked_by` and `checked_on`.
  - Every office has a source.
  - Every promise row points to a real candidate and a known `kind`.
  - Each race is marked **live** only if it has no draft quotes. Otherwise it is "being reviewed".
- **Tests:** `node --test`. Each fixture must fail for its reason: a missing topic, a 61-word quote, an extra candidate, a draft quote in a live race.
- **Learn:** turning a promise like "we treat everyone the same" into code that refuses to break it.
- **Done when:** the fixtures fail, the real data passes, and `npm run build` runs the check.

---

## Days 2–3 (Oct 14–16): the walk

### Task 6: Ward map component
- **Files:** `site/src/lib/vote/VoteMap.svelte`, reusing `site/src/lib/geo/wards.json` and the GeoJSON winding fix from `StoryMap.svelte`.
- **Builds:**
  - Wards 20–25 drawn with d3-geo, then smoothed (simplify, then Chaikin rounding, as in the mockup).
  - The flowing gradient on your ward, a tint of the room colour on the other wards, the self-drawing route, the travelling dot, pulsing and visited stops.
  - Tapping a ward selects it. Wards are keyboard-focusable with labels.
  - Under `prefers-reduced-motion`, everything is static.
- **Learn:** map projections, SVG paths, and animating with CSS variables.
- **Done when:** it matches the mockup at 390px and 1280px widths.

### Task 7: `/vote` page: entrance, ticket, rooms, plaques
- **Files:**
  - `site/src/routes/vote/+page.svelte` and `+page.server.ts`.
  - Components in `site/src/lib/vote/`: `Ticket.svelte`, `Room.svelte`, `Plaque.svelte`, `NothingLine.svelte`.
- **Builds:**
  - The ticket has a **My ward / Mayor** choice, ward buttons, a postal-code lookup (reusing `RepLookup`) and a link to the City list for readers outside Scarborough.
  - An IntersectionObserver works out which room you're in.
  - Rooms are driven by `topics.yaml`. Big numbers use `<Fact>`.
  - Plaques are in ballot order. **`Plaque` has no colour prop.**
  - The "Nothing published on this yet: …" line.
  - A race that isn't live shows "This race is being reviewed" with names only.
  - Getting around shows the TTC and Transportation Services ($516M).
- **Learn:** Svelte 5 components and props, and scroll-driven UI.
- **Done when:** the whole walk works with test data for one ward and the mayor's race.

### Task 8: "What if they do it?" panels
- **Files:** `site/src/lib/vote/whatif/TaxWhatIf.svelte`, `HomesWhatIf.svelte`, `FareWhatIf.svelte` and `OfficersWhatIf.svelte`.
- **Rules (spec §4.4):**
  - A panel appears only when `promises.yaml` has **checked** rows for that room.
  - Candidates are shown in ballot order.
  - The panel shows the campaign's exact wording, with the fixed caption.
  - It does arithmetic only. The tax panel takes a bill, a rate rule and an inflation slider; the homes panel shows 650 dots against the 65,000 target.
  - `OfficersWhatIf` only appears if a checked TPS officer-count fact exists.
- **Tests:** unit tests for the tax arithmetic, covering freeze, inflation and a fixed percentage.
- **Learn:** making numbers interactive without making claims.
- **Done when:** the tax and homes panels work from `promises.yaml` test rows.

### Task 9: Passport, pins and share
- **Files:** `site/src/lib/vote/Passport.svelte`, `MyWalk.svelte` and `pins.ts`.
- **Builds:**
  - Stamps for visited rooms.
  - Pins saved in `localStorage`, wrapped in try/catch so the page still works if storage is blocked.
  - At the exit, the Your walk card.
  - A share button using `navigator.share`, falling back to copying the link. It shares neutral text only.
- **Done when:** pins survive a reload, and the network panel shows that nothing is sent.

### Task 10: Race pages
- **Files:** `site/src/routes/vote/[race]/+page.svelte`, `+page.server.ts` and `+page.ts` (prerender entries for the 7 races).
- **Builds:**
  - Full candidate cards in ballot order.
  - Incumbents' votes, from `people.yaml` by matching `id`.
  - A "Compare one topic" switch.
  - Ward money from `wards.json`.
  - The "being reviewed" state.
- **Done when:** all 7 pages prerender.

### Task 11: Header, sharing tags and corrections
- **Files:**
  - `site/src/routes/+layout.svelte`: nav becomes **2026 Election · Scarborough · Toronto · Ontario**, plus the existing pages. Election is first and highlighted.
  - `/vote` head: Open Graph and Twitter tags, plus a static share image (`site/static/og-vote.png`, 1200×630, showing the title and the blue/orange/green ribbon) so the LinkedIn preview looks right.
  - Footer: "Something wrong?" links to the project email.
- **Done when:** LinkedIn's Post Inspector (or an OG preview tool) shows the card. This is checked after hosting is set up.

---

## Days 2–5 (Oct 14–17, in parallel): gathering

### Task 12: Review tool (dev only)
- **Files:**
  - `site/src/routes/review/+page.svelte`.
  - `site/src/routes/review/+server.ts`, which writes the YAML.
  - Both guarded by `dev` from `$app/environment`, and set to `prerender = false`.
  - The build check fails if `/review` ends up in `build/`.
- **Builds:**
  - A list of draft quotes and promises, each with its source and archive links.
  - **Approve** sets `checked`, `checked_by` and `checked_on`.
  - **Reject** removes the item and appends the reason to `data/candidates/review-log.yaml`.
- **Learn:** a small local admin tool, and why it must never ship.
- **Done when:** approving a quote updates the YAML, and `npm run build` contains no `/review`.

### Task 13: Gathering quotes (Claude)
- **Order:** the mayor's race first, then wards 20 to 25.
- For each candidate:
  1. Find their official site and socials.
  2. Read the platform.
  3. Draft up to 2 quotes per topic, using the on-topic rules from `topics.yaml`.
  4. Save each source to the Internet Archive and record the archive link.
  5. Record past offices with sources.
  6. Add promise rows for promises that have a number.
- Start from `research/mayor-2026.md`, and **re-source every item from the candidate's own site or City records**, never from news or Wikipedia alone.
- Commit after each race.
- **Done when:** every candidate in all 7 races has been researched, including those who end up as "nothing published".

---

## Oct 15–20: review and launch

### Task 14: Review (you)
- Work through `/review`, mayor's race first. It takes about 15–20 minutes per candidate with published material, and 25–35 hours in total.
- **A race goes live once its last quote is checked.**

### Task 15: Tests
- Playwright (Python, `uv run --with playwright==1.58.0`, in `tests/test_site.py`):
  - `/vote` at 390px and 1280px with no horizontal scroll.
  - The ticket switches ward and race.
  - Rooms activate on scroll.
  - Reduced motion is respected.
  - Ballot order on race pages.
  - The tax panel arithmetic.
  - Pins persist after a reload.
  - `/review` is absent from the build.
- `npm run check`, the content and candidate checks, and the pipeline tests must all pass.

### Task 16: Launch
- **You:**
  - Call the City Clerk's elections office to confirm a free, equal-treatment guide isn't third-party advertising, and note their answer in `research/`.
  - Create the corrections email address.
- **Claude:**
  - Set up hosting. Netlify or Cloudflare Pages both work for a static build, free; we pick when you create the account.
  - Push to GitHub, deploy, and check the OG card.
- Soft launch, then a LinkedIn post. **Don't pay to boost it.**

### Task 17: Final week (Oct 23)
- Re-run `pipeline.candidates` for withdrawals.
- Re-check candidate sites for changes; changed quotes go back to draft.
- Redeploy.

---

## Cut list (if we fall behind, drop these in this order)
1. `FareWhatIf` and `OfficersWhatIf`.
2. The "Compare one topic" switch.
3. The passport and pins. The share button stays.
4. Ward pages beyond the ones fully reviewed (launch the mayor's race plus finished wards).

**Never cut:** the fairness checks, the review gate, the archive links, the captions on the what-if panels.
