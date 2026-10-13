"""Download every raw source, unchanged, into data/raw/ and write data/sources.json.

CKAN resources are resolved through the Toronto Open Data `package_show` API so
that new resource IDs are picked up automatically.

Usage:
    uv run python -m pipeline.fetch            # download anything missing
    uv run python -m pipeline.fetch --force    # re-download everything
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys

import requests

from .common import (
    BUDGET_SUMMARY_TITLE,
    BUDGET_SUMMARY_URL,
    ONTARIO_BUDGET_CH3_URL,
    RAW,
    ROOT,
    SOURCES_JSON,
    load_sources,
)

CKAN = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show"
HEADERS = {"User-Agent": "follow-the-budget-pipeline/0.1 (public-interest research)"}

CAPITAL_PKG = "budget-capital-budget-plan-by-ward-10-yr-approved"
OPERATING_PKG = "budget-operating-budget-program-summary-by-expenditure-category"
WARD_PROFILES_PKG = "ward-profiles-25-ward-model"
WARDS_PKG = "city-wards"
POLICE_PKG = "toronto-police-budget"
VOTES_PKG = "members-of-toronto-city-council-voting-record"

# 25-ward capital files begin with the 2019-2028 plan.
CAPITAL_FIRST_YEAR = 2019
OPERATING_YEARS = range(2019, 2026)


def package(pkg_id: str) -> dict:
    r = requests.get(CKAN, params={"id": pkg_id}, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r.json()["result"]


def ext_of(url: str, fmt: str) -> str:
    m = re.search(r"\.([A-Za-z0-9]{2,7})$", url.split("?")[0])
    return (m.group(1) if m else fmt).lower()


def targets() -> list[dict]:
    """Return the list of {id,title,url,ext} to download."""
    out: list[dict] = []

    out.append(
        {
            "id": "toronto-budget-summary-2026",
            "title": BUDGET_SUMMARY_TITLE + " (PDF)",
            "url": BUDGET_SUMMARY_URL,
            "ext": "pdf",
        }
    )

    out.append(
        {
            "id": "ontario-budget-2026-ch3",
            "title": "2026 Ontario Budget, Chapter 3: Ontario's Fiscal Plan and Outlook (HTML tables)",
            "url": ONTARIO_BUDGET_CH3_URL,
            "ext": "html",
        }
    )

    pkg = package(CAPITAL_PKG)
    for res in pkg["resources"]:
        name = res["name"].strip()
        m = re.match(r"^(\d{4})-(?:to-)?(\d{4})-capital-budget-(?:and-plan-details|plan-by-ward)$", name)
        if not m:
            continue
        start = int(m.group(1))
        if start < CAPITAL_FIRST_YEAR:
            continue
        out.append(
            {
                "id": f"toronto-capital-{start}",
                "title": f"{pkg['title']}: {start}-{m.group(2)}",
                "url": res["url"],
                "ext": ext_of(res["url"], res["format"]),
            }
        )

    pkg = package(OPERATING_PKG)
    for res in pkg["resources"]:
        m = re.match(r"^approved-operating-budget-summary-(\d{4})$", res["name"].strip())
        if m and int(m.group(1)) in OPERATING_YEARS:
            out.append(
                {
                    "id": f"toronto-operating-{m.group(1)}",
                    "title": f"{pkg['title']}: {m.group(1)} approved",
                    "url": res["url"],
                    "ext": ext_of(res["url"], res["format"]),
                }
            )

    pkg = package(WARD_PROFILES_PKG)
    for res in pkg["resources"]:
        if res["name"].strip() == "2023-WardProfiles-2011-2021-CensusData":
            out.append(
                {
                    "id": "toronto-ward-profiles-2021",
                    "title": f"{pkg['title']}: 2011-2021 Census data",
                    "url": res["url"],
                    "ext": ext_of(res["url"], res["format"]),
                }
            )

    pkg = package(WARDS_PKG)
    for res in pkg["resources"]:
        if res["name"].strip() == "City Wards Data - 4326.geojson":
            out.append(
                {
                    "id": "toronto-wards-geojson",
                    "title": f"{pkg['title']} (WGS84 GeoJSON)",
                    "url": res["url"],
                    "ext": "geojson",
                }
            )

    pkg = package(POLICE_PKG)
    for res in pkg["resources"]:
        m = re.match(r"^TPS Budget (\d{4})\.csv$", res["name"].strip())
        if m:
            out.append(
                {
                    "id": f"toronto-police-budget-{m.group(1)}",
                    "title": f"{pkg['title']}: {m.group(1)}",
                    "url": res["url"],
                    "ext": "csv",
                }
            )

    pkg = package(VOTES_PKG)
    for res in pkg["resources"]:
        if res["name"].strip() == "member-voting-record-2022-2026" and res.get("datastore_active"):
            out.append(
                {
                    "id": "toronto-council-votes-2022-2026",
                    "title": f"{pkg['title']}: 2022-2026 term",
                    "url": res["url"],
                    "ext": "csv",
                }
            )

    out.sort(key=lambda t: t["id"])
    ids = [t["id"] for t in out]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise RuntimeError(f"duplicate source ids: {dupes}")
    expected = (
        {f"toronto-capital-{y}" for y in range(CAPITAL_FIRST_YEAR, 2027)}
        | {f"toronto-operating-{y}" for y in OPERATING_YEARS}
        | {"toronto-ward-profiles-2021", "toronto-wards-geojson", "toronto-budget-summary-2026",
           "ontario-budget-2026-ch3", "toronto-council-votes-2022-2026"}
    )
    missing = expected - set(ids)
    if missing:
        raise RuntimeError(f"could not resolve sources: {sorted(missing)}")
    return out


def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest) -> None:
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, headers=HEADERS, timeout=300, stream=True) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    tmp.replace(dest)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true", help="re-download files that already exist")
    args = ap.parse_args(argv)

    RAW.mkdir(parents=True, exist_ok=True)
    previous = {s["id"]: s for s in load_sources()}
    manifest = []
    for t in targets():
        dest = RAW / f"{t['id']}.{t['ext']}"
        prev = previous.get(t["id"])
        if args.force or not dest.exists():
            print(f"fetch {t['id']} <- {t['url']}", file=sys.stderr)
            download(t["url"], dest)
            fetched_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
        else:
            fetched_at = prev["fetchedAt"] if prev else dt.datetime.fromtimestamp(
                dest.stat().st_mtime, dt.timezone.utc
            ).replace(microsecond=0).isoformat()
        digest = sha256(dest)
        if prev and prev.get("sha256") != digest and not args.force and dest.exists():
            # file on disk changed since the manifest was written
            fetched_at = dt.datetime.fromtimestamp(dest.stat().st_mtime, dt.timezone.utc).replace(
                microsecond=0
            ).isoformat()
        manifest.append(
            {
                "id": t["id"],
                "title": t["title"],
                "url": t["url"],
                "fetchedAt": fetched_at,
                "sha256": digest,
                "file": str(dest.relative_to(ROOT)),
            }
        )
    SOURCES_JSON.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {SOURCES_JSON.relative_to(ROOT)} ({len(manifest)} sources)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
