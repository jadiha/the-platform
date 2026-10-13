"""Build the City of Toronto and Scarborough outputs (docs/data-contract.md).

Writes:
  data/clean/budget-toronto-2026.json      2026 operating budget, by shared category
  data/clean/budget-scarborough-2026.json  ward-tagged 10-year capital plan, wards 20-25
  data/clean/wards.json                    capital per resident for all 25 wards
  data/clean/trends-toronto.json           approved operating budgets 2019-2025

Usage:
    uv run python -m pipeline.toronto
"""
from __future__ import annotations

import csv
from collections import defaultdict

import pandas as pd

from . import budget_summary
from .budget_summary import norm_label
from .common import (
    BUDGET_SUMMARY_TITLE,
    BUDGET_SUMMARY_URL,
    CATEGORIES,
    CATEGORY_NAMES,
    CLEAN,
    MAPPINGS,
    SCARBOROUGH_WARDS,
    r1,
    raw_path,
    source,
    write_json,
)

CAPITAL_ID = "toronto-capital-2026"
PROFILES_ID = "toronto-ward-profiles-2021"
WARDS_GEO_ID = "toronto-wards-geojson"
TREND_YEARS = range(2019, 2026)
EXCLUDE = "EXCLUDE"
# Fee-funded programs. Left out of trends: from 2022 the Open Data files stopped counting
# Toronto Water's transfer to its own capital as an expense ($1.4B -> $0.47B), a basis change.
RATE_PROGRAMS = {"toronto water", "solid waste management services", "toronto parking authority"}


def load_mapping() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in csv.DictReader(open(MAPPINGS / "toronto.csv", newline="")):
        key = row["original_line"]
        if key in out:
            raise ValueError(f"toronto.csv: {key!r} mapped twice")
        if row["category"] not in CATEGORIES and row["category"] != EXCLUDE:
            raise ValueError(f"toronto.csv: {key!r} has unknown category {row['category']!r}")
        out[key] = row
    return out


def category_of(mapping: dict, label: str) -> str:
    key = norm_label(label)
    if key not in mapping:
        raise KeyError(f"no category for Toronto line {label!r} (normalised {key!r}); add it to data/mappings/toronto.csv")
    return mapping[key]["category"]


def _pdf_source(locator: str) -> dict:
    return {"title": BUDGET_SUMMARY_TITLE, "url": BUDGET_SUMMARY_URL, "locator": locator}


def _category_nodes(prefix: str, leaves: list[dict]) -> list[dict]:
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for leaf in leaves:
        by_cat[leaf.pop("_cat")].append(leaf)
    nodes = []
    for cat, kids in by_cat.items():
        kids.sort(key=lambda k: -k["gross"])
        nets = [k.get("net") for k in kids]
        nodes.append(
            {
                "id": f"{prefix}.{cat}",
                "name": CATEGORY_NAMES[cat],
                "category": cat,
                "gross": r1(sum(k["gross"] for k in kids)),
                "net": r1(sum(nets)) if all(n is not None for n in nets) else None,
                "originalLines": [k["name"] for k in kids],
                "children": kids,
            }
        )
    nodes.sort(key=lambda n: -n["gross"])
    return nodes


# ---------------------------------------------------------------- operating 2026

def build_operating(mapping: dict) -> dict:
    bs = budget_summary.get()
    app = bs["appendix"]
    gross_rows, net_rows, rev_rows = (app[k]["rows"] for k in ("gross", "net", "revenue"))

    def by_label(rows: dict) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for key, r in rows.items():
            if key.startswith(("total|", "corporate-subtotal|")):
                continue
            out[norm_label(r["label"])] = r
        return out

    net_by, rev_by = by_label(net_rows), by_label(rev_rows)
    leaves = []
    for key, r in gross_rows.items():
        if key.startswith(("total|", "corporate-subtotal|")):
            continue
        cat = category_of(mapping, r["label"])
        if cat == EXCLUDE:
            continue
        lab = norm_label(r["label"])
        if r["section"] == "non-levy":
            # Rate programs (water, garbage, parking) are counted in the $18.9B at their full
            # budget, which includes what they set aside for their own capital work. That
            # equals their revenue (Appendix 1.1.3); Appendix 1.1.2 shows a smaller "gross".
            src = rev_by[lab]
            locator = f"Appendix 1.1.3 (revenues), p. {src['page']}"
        else:
            src = r
            locator = f"Appendix 1.1.2 (gross expenditures), p. {r['page']}"
        gross = src["values"].get("b2026")
        if gross is None:
            continue
        net = net_by.get(lab, {}).get("values", {}).get("b2026")
        note = mapping[lab]["notes"] or None
        leaves.append(
            {
                "id": f"toronto.{lab.replace(' ', '-')}",
                "name": r["label"].replace(" - ", " – "),
                "_cat": cat,
                "gross": r1(gross / 1000),
                "net": r1(net / 1000) if net is not None else None,
                "note": note,
                "source": _pdf_source(locator),
            }
        )

    children = _category_nodes("toronto", leaves)
    total = r1(sum(c["gross"] for c in children))
    fig1 = bs["figure1"]
    official = sum(i["value"] for i in fig1["items"])
    # Figure 1 items are rounded to whole $M, so allow a few $M of rounding.
    if abs(total - official) > 5:
        raise AssertionError(f"Toronto tree total {total} != official Figure 1 total {official}")
    return {
        "id": "toronto",
        "name": "City of Toronto",
        "year": "2026",
        "basis": "gross, approved operating budget (tax and rate supported)",
        "gross": total,
        "net": None,
        "note": "Water, garbage and parking are paid for by user fees, not property tax. They are shown at their full budget, as in the City's $18.9 billion total.",
        "source": _pdf_source(f"Figure 1 (p. {fig1['page']}); Appendices 1.1.1–1.1.3"),
        "children": children,
    }


# ---------------------------------------------------------------- capital by ward

def load_capital() -> pd.DataFrame:
    df = pd.read_excel(raw_path(CAPITAL_ID), header=0)
    df.columns = [str(c).replace(".0", "").strip() for c in df.columns]
    df["Ward"] = df["Ward"].astype(str).str.strip()
    df["Program"] = df["Program"].astype(str).str.strip()
    df["Project Name"] = df["Project Name"].astype(str).str.strip()
    return df


def ward_populations() -> dict[int, int]:
    w = pd.read_excel(raw_path(PROFILES_ID), "2021 One Variable", header=None)
    header = w.iloc[17].tolist()
    row = w[w[0].astype(str).str.strip() == "Total - Age"].iloc[0]
    out = {}
    for i, h in enumerate(header):
        if isinstance(h, str) and h.startswith("Ward "):
            out[int(h.split()[1])] = int(row[i])
    if len(out) != 25:
        raise ValueError(f"expected 25 wards in ward profiles, got {len(out)}")
    return out


def ward_names() -> dict[int, str]:
    import json

    g = json.loads(raw_path(WARDS_GEO_ID).read_text())
    return {int(f["properties"]["AREA_SHORT_CODE"]): f["properties"]["AREA_NAME"] for f in g["features"]}


def build_wards(mapping: dict, cap: pd.DataFrame) -> dict:
    bs = budget_summary.get()
    pops, names = ward_populations(), ward_names()
    total10 = cap["10-Year Total"].sum() / 1000
    official = bs["capital"]["capital10yrGross"]
    if abs(total10 - official) > 1:
        raise AssertionError(f"capital file total {total10:.1f} != Budget Summary {official:.1f}")
    cw = cap[cap["Ward"] == "CW"]["10-Year Total"].sum() / 1000

    wards = []
    for ward in range(1, 26):
        rows = cap[cap["Ward"] == str(ward)]
        projects = (
            rows.groupby(["Program", "Project Name"])["10-Year Total"].sum().sort_values(ascending=False) / 1000
        )
        c10 = rows["10-Year Total"].sum() / 1000
        wards.append(
            {
                "ward": ward,
                "name": names[ward],
                "scarborough": ward in SCARBOROUGH_WARDS,
                "population": pops[ward],
                "capital10yr": r1(c10),
                "capital2026": r1(rows["2026"].sum() / 1000),
                "perResident10yr": r1(c10 * 1e6 / pops[ward]),
                "topProjects": [
                    {"name": proj, "program": prog, "amount10yr": r1(v), "category": category_of(mapping, prog)}
                    for (prog, proj), v in projects.head(5).items()
                ],
            }
        )
    return {
        "asOf": source(CAPITAL_ID)["fetchedAt"][:10],
        "capitalPlan": "2026–2035",
        "populationSource": "2021 Census, persons in private households (City of Toronto Ward Profiles)",
        "cityWide": {"capital10yr": r1(cw), "share": round(cw / total10, 3)},
        "total10yr": r1(total10),
        "wards": wards,
    }


def build_scarborough(mapping: dict, cap: pd.DataFrame) -> dict:
    rows = cap[cap["Ward"].isin([str(w) for w in SCARBOROUGH_WARDS])]
    grouped = rows.groupby(["Program", "Project Name"])["10-Year Total"].sum() / 1000
    wards_of = rows.groupby(["Program", "Project Name"])["Ward"].agg(lambda s: sorted(set(s), key=int))
    leaves = []
    for (prog, proj), v in grouped.items():
        if abs(v) < 0.05:
            continue
        leaves.append(
            {
                "id": f"scarborough.{norm_label(prog + ' ' + proj).replace(' ', '-')}",
                "name": proj,
                "_cat": category_of(mapping, prog),
                "gross": r1(v),
                "net": None,
                "note": f"{prog}. Ward {', '.join(wards_of[(prog, proj)])}.",
            }
        )
    children = _category_nodes("scarborough", leaves)
    for c in children:
        c["net"] = None
    return {
        "id": "scarborough",
        "name": "Scarborough (Wards 20–25)",
        "year": "2026",
        "basis": "10-year capital plan 2026–2035, ward-tagged projects only",
        "gross": r1(sum(c["gross"] for c in children)),
        "net": None,
        "note": "Only projects the City tags to a Scarborough ward. Most capital money (TTC, police, water systems) is tagged 'City Wide' and can't be split by neighbourhood, so Scarborough benefits from more than this.",
        "source": {
            "title": source(CAPITAL_ID)["title"],
            "url": source(CAPITAL_ID)["url"],
            "locator": "rows with Ward 20–25",
        },
        "children": children,
    }


# ---------------------------------------------------------------- trends

def load_operating(year: int) -> pd.DataFrame:
    """Open Data operating files have varying sheet names and header rows."""
    x = pd.ExcelFile(raw_path(f"toronto-operating-{year}"))
    for sheet in x.sheet_names:
        if sheet.startswith("_com"):
            continue
        head = pd.read_excel(x, sheet, header=None, nrows=15)
        for i in range(len(head)):
            cells = [str(v).strip() for v in head.iloc[i].tolist()]
            if "Program" in cells and "Expense/Revenue" in cells:
                df = pd.read_excel(x, sheet, header=i)
                df.columns = [str(c).strip() for c in df.columns]
                return df
    raise ValueError(f"no data sheet found in toronto-operating-{year}")


def build_trends(mapping: dict) -> dict:
    series: dict[str, list[dict]] = defaultdict(list)
    for year in TREND_YEARS:
        df = load_operating(year)
        col = str(year)
        df = df[df["Program"].notna() & (df["Expense/Revenue"].astype(str).str.strip() == "Expenses")]
        df = df[df["Program"].astype(str).str.strip() != "0"]
        totals: dict[str, float] = defaultdict(float)
        for prog, v in df.groupby("Program")[col].sum().items():
            if norm_label(str(prog)) in RATE_PROGRAMS:
                continue
            cat = category_of(mapping, str(prog))
            if cat != EXCLUDE:
                totals[cat] += v / 1e6
        for cat in CATEGORIES:
            if cat in totals:
                series[cat].append(
                    {"year": str(year), "value": r1(totals[cat]), "kind": "plan", "sourceRef": f"toronto-operating-{year}"}
                )
    return {
        "toronto": dict(series),
        "toronto-notes": [
            "Approved operating budgets, gross expenditures, from the City's Open Data 'Operating Budget Program Summary' files (2019–2025).",
            "Tax-supported programs only. Water, garbage and parking are left out because the way their spending is reported changed in 2022.",
            "These files include internal charges between City divisions, so their totals are higher than the City's headline budget. They are used for direction of change only.",
            "2026 is not included because it has not been published in this format; 2026 figures elsewhere on the site come from the 2026 Budget Summary.",
        ],
    }


def main() -> int:
    mapping = load_mapping()
    cap = load_capital()
    write_json(CLEAN / "budget-toronto-2026.json", build_operating(mapping))
    write_json(CLEAN / "budget-scarborough-2026.json", build_scarborough(mapping, cap))
    write_json(CLEAN / "wards.json", build_wards(mapping, cap))
    write_json(CLEAN / "trends-toronto.json", build_trends(mapping))
    print("wrote Toronto outputs to data/clean/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
