"""The City Clerk's certified candidate list -> data/clean/candidates-official.json.

The Clerk's page (https://www.toronto.ca/city-government/elections/candidate-list/) builds its
tables with JavaScript, so the raw file is a snapshot of those tables taken with a headless
browser (see `snapshot()`), saved to data/raw/toronto-candidates-2026.json. Table 0 is Mayor.

Ballot order is alphabetical by last name, exactly as the Clerk lists it. Nothing here reorders it.

Usage:
    uv run --with playwright==1.58.0 python -m pipeline.candidates --snapshot   # refresh raw
    uv run python -m pipeline.candidates
"""
from __future__ import annotations

import json
import sys

from .common import CLEAN, RAW, write_json

LIST_URL = "https://www.toronto.ca/city-government/elections/candidate-list/"
RAW_FILE = RAW / "toronto-candidates-2026.json"
SOCIAL = ("instagram", "x.com", "facebook", "tiktok", "threads", "linkedin", "youtube", "substack", "toronto.ca")


def snapshot() -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page()
        p.goto(LIST_URL, wait_until="networkidle")
        rows = p.evaluate(
            """() => [...document.querySelectorAll('table')].map(t => [...t.querySelectorAll('tbody tr')]
                 .map(r => ({cells: [...r.cells].map(c => c.innerText.trim()), links: [...r.querySelectorAll('a')].map(a => a.href)})))"""
        )
        b.close()
    RAW_FILE.write_text(json.dumps(rows, indent=0))
    print(f"wrote {RAW_FILE.relative_to(RAW.parent.parent)}")


def parse_row(row: dict) -> dict:
    last, _, first = row["cells"][0].partition(", ")
    links = [link for link in row["links"] if link.startswith("http")]
    return {
        "ballot_name": row["cells"][0],
        "name": f"{first} {last}".strip(),
        "website": next((link for link in links if not any(s in link for s in SOCIAL)), None),
        "social": [link for link in links if any(s in link for s in SOCIAL[:-1])],
        "nominated": row["cells"][-1],
    }


def build() -> dict:
    tables = json.loads(RAW_FILE.read_text())
    mayor = [parse_row(r) for r in tables[0]]
    if not 40 <= len(mayor) <= 120:
        raise AssertionError(f"mayor table has {len(mayor)} rows; the page layout may have changed")
    return {"source": {"title": "City of Toronto, 2026 certified candidate list", "url": LIST_URL}, "mayor": mayor}


def main(argv: list[str] | None = None) -> int:
    if "--snapshot" in (argv or sys.argv[1:]):
        snapshot()
    write_json(CLEAN / "candidates-official.json", build())
    print("wrote data/clean/candidates-official.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
