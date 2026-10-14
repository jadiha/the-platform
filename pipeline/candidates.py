"""The City Clerk's certified candidate list -> data/clean/candidates-official.json.

The Clerk's page (https://www.toronto.ca/city-government/elections/candidate-list/) builds its
tables with JavaScript, so the raw file is a snapshot of those tables taken with a headless
browser (see `snapshot()`), saved to data/raw/toronto-candidates-2026.json: one entry per table,
with the heading the Clerk puts above it ("Candidates for Mayor", "Councillor Ward 1 - ...",
"Toronto District School Board Ward 1", ...).

School board wards don't match city wards. Which city wards each trustee ward covers comes from the
Clerk's "2026 School Board Reference Chart" (SCHOOL_CHART below, typed from the PDF).

Ballot order is alphabetical by last name, exactly as the Clerk lists it. Nothing here reorders it.

Usage:
    uv run --with playwright==1.58.0 python -m pipeline.candidates --snapshot   # refresh raw
    uv run python -m pipeline.candidates
"""
from __future__ import annotations

import json
import re
import sys

from .common import CLEAN, RAW, write_json

LIST_URL = "https://www.toronto.ca/city-government/elections/candidate-list/"
RAW_FILE = RAW / "toronto-candidates-2026.json"
SOCIAL = ("instagram", "x.com", "facebook", "tiktok", "threads", "linkedin", "youtube", "substack", "toronto.ca")


def snapshot() -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36")
        p.goto(LIST_URL, wait_until="networkidle")
        p.wait_for_timeout(3000)
        rows = p.evaluate(
            """() => [...document.querySelectorAll('table')].map(t => {
                 let e = t, h = '';
                 for (let k = 0; k < 40 && !h; k++) {
                   e = e.previousElementSibling || e.parentElement; if (!e) break;
                   const q = e.matches('h2,h3,h4,h5') ? e : [...e.querySelectorAll('h2,h3,h4,h5')].pop();
                   if (q) h = q.innerText.trim();
                 }
                 return {heading: h, rows: [...t.querySelectorAll('tbody tr')]
                   .map(r => ({cells: [...r.cells].map(c => c.innerText.trim()), links: [...r.querySelectorAll('a')].map(a => a.href)}))};
               })"""
        )
        b.close()
    RAW_FILE.write_text(json.dumps(rows, indent=0))
    print(f"wrote {RAW_FILE.relative_to(RAW.parent.parent)}")


def parse_row(row: dict) -> dict:
    last, _, first = row["cells"][0].partition(", ")
    links = [link for link in row["links"] if link.startswith("http")]
    return {
        "ballot_name": row["cells"][0],
        # The Clerk's list has the odd stray comma (e.g. "Nisha Kumari,"); ballot_name keeps it verbatim.
        "name": f"{first} {last}".strip(" ,"),
        "website": next((link for link in links if not any(s in link for s in SOCIAL)), None),
        "social": [link for link in links if any(s in link for s in SOCIAL[:-1])],
        "nominated": row["cells"][-1],
    }


CHART_URL = "https://www.toronto.ca/wp-content/uploads/2026/04/9600-2026-School-board-ward-reference-chart.pdf"
# board heading prefix -> (short name, plain-language name, {trustee ward: city wards})
SCHOOL_CHART = {
    "Toronto District School Board": ("TDSB", "English public", {
        "1": [1, 7], "2": [2, 3], "3": [4, 9], "4": [6, 18], "5": [10, 14], "6": [5, 8],
        "7": [11, 12, 13], "8": [15, 16], "9": [17, 22], "10": [19, 20], "11": [21, 23], "12": [24, 25]}),
    "Toronto Catholic District School Board": ("TCDSB", "English Catholic", {
        "1": [1], "2": [2], "3": [7], "4": [3, 4], "5": [6, 8, 18], "6": [9], "7": [21, 22], "8": [23, 25],
        "9": [10, 11, 12, 13], "10": [5], "11": [14, 15, 16, 17, 19], "12": [20, 24]}),
    "Conseil scolaire Viamonde": ("Viamonde", "French public", {
        "2 - Est": [6, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25], "3 - Centre": [10, 11, 12, 13, 14, 19],
        "4 - Ouest": [1, 2, 3, 4, 5, 7, 8, 9]}),
    "Conseil scolaire catholique MonAvenir": ("MonAvenir", "French Catholic", {
        "3 - Toronto Ouest": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18],
        "4 - Toronto Est": [14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25]}),
}


def build() -> dict:
    tables = json.loads(RAW_FILE.read_text())
    by_heading = {t["heading"]: t["rows"] for t in tables}
    mayor = [parse_row(r) for r in by_heading["Candidates for Mayor"]]
    if not 40 <= len(mayor) <= 120:
        raise AssertionError(f"mayor table has {len(mayor)} rows; the page layout may have changed")

    wards = []
    for h, rows in by_heading.items():
        m = re.fullmatch(r"Councillor Ward (\d+) - (.+)", h)
        if m:
            wards.append({"ward": int(m[1]), "name": m[2], "councillor": [parse_row(r) for r in rows], "trustees": []})
    wards.sort(key=lambda w: w["ward"])
    if [w["ward"] for w in wards] != list(range(1, 26)):
        raise AssertionError("expected councillor tables for wards 1-25")

    seen = set()
    for h, rows in by_heading.items():
        for prefix, (short, kind, chart) in SCHOOL_CHART.items():
            m = re.fullmatch(re.escape(prefix) + r" Ward (.+)", h)
            if not m or m[1] not in chart:
                continue
            seen.add((short, m[1]))
            for city_ward in chart[m[1]]:
                wards[city_ward - 1]["trustees"].append({
                    "board": short, "kind": kind, "board_ward": m[1].split(" - ")[0],
                    "candidates": [parse_row(r) for r in rows],
                })
    missing = [(s, w) for _, (s, _, c) in SCHOOL_CHART.items() for w in c if (s, w) not in seen]
    # Viamonde Ward 2/3/4 and MonAvenir 3/4 are all on the list; a missing one means the page changed.
    if missing:
        raise AssertionError(f"no candidate table for trustee wards {missing}")
    for w in wards:
        if len({t["board"] for t in w["trustees"]}) != 4:
            raise AssertionError(f"ward {w['ward']} should have one trustee race on each of the 4 boards")

    return {
        "source": {"title": "City of Toronto, 2026 certified candidate list", "url": LIST_URL},
        "school_chart": {"title": "City of Toronto, 2026 School Board Reference Chart", "url": CHART_URL},
        "mayor": mayor,
        "wards": wards,
    }


def main(argv: list[str] | None = None) -> int:
    if "--snapshot" in (argv or sys.argv[1:]):
        snapshot()
    write_json(CLEAN / "candidates-official.json", build())
    print("wrote data/clean/candidates-official.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
