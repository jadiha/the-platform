"""Build the Province of Ontario budget tree from the 2026 Ontario Budget, Table 3.10.

Writes data/clean/budget-ontario-2026-27.json: total expense, by shared category,
then by ministry, then by the sub-lines the Budget publishes for that ministry.

Usage:
    uv run python -m pipeline.ontario
"""
from __future__ import annotations

import csv
import io
import re
from collections import defaultdict

import pandas as pd

from .common import CATEGORIES, CATEGORY_NAMES, CLEAN, MAPPINGS, ONTARIO_BUDGET_TITLE, r1, raw_path, source, write_json

SOURCE_ID = "ontario-budget-2026-ch3"
PLAN_COL = "Plan 2026–27"
OFFICIAL_TOTAL = 244200.0  # Table 3.1 / 3.12, $M; also asserted against the table's own total row


def _clean_label(s: str) -> str:
    s = re.sub(r"\s+", " ", str(s)).strip()
    return re.sub(r"(\))\d+$|(?<=[a-z])\d+$", r"\1", s)  # strip footnote markers


def _num(v) -> float:
    s = str(v).strip().replace(",", "")
    if s in ("–", "-", "—", "", "nan"):
        return 0.0
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    return -float(s) if neg else float(s)


def table_3_10() -> pd.DataFrame:
    html = raw_path(SOURCE_ID).read_text()
    for t in pd.read_html(io.StringIO(html)):
        if str(t.columns[0]).strip() == "Ministry Expense":
            t.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in t.columns]
            return t
    raise ValueError("Table 3.10 (Ministry Expense) not found in chapter 3 HTML")


def load_mapping() -> dict[str, dict]:
    out = {}
    for row in csv.DictReader(open(MAPPINGS / "ontario.csv", newline="")):
        if row["category"] not in CATEGORIES:
            raise ValueError(f"ontario.csv: unknown category {row['category']!r}")
        if row["original_line"] in out:
            raise ValueError(f"ontario.csv: {row['original_line']!r} mapped twice")
        out[row["original_line"]] = row
    return out


def build() -> dict:
    mapping = load_mapping()
    t = table_3_10()
    src = source(SOURCE_ID)
    ref = {"title": ONTARIO_BUDGET_TITLE, "url": src["url"]}

    ministries: list[dict] = []
    pending: list[tuple[str, float]] = []
    table_total = None
    for _, row in t.iterrows():
        label = _clean_label(row["Ministry Expense"])
        value = _num(row[PLAN_COL])
        if label == "Total Expense":
            table_total = value
            continue
        if label.endswith("(Total)") or label.startswith("Interest and Other Debt"):
            if label not in mapping:
                raise KeyError(f"Ontario line {label!r} is not in data/mappings/ontario.csv")
            name = label.removesuffix(" (Total)")
            subs = [
                {
                    "id": f"ontario.{_slug(name)}.{_slug(sub)}",
                    "name": "Core ministry spending" if sub.endswith("(Base)") else sub.split(" — ", 1)[-1],
                    "gross": r1(v),
                }
                for sub, v in pending
                if abs(v) >= 0.05
            ]
            if subs and abs(sum(s["gross"] for s in subs) - value) > 0.5:
                raise AssertionError(f"{label}: sub-lines sum {sum(s['gross'] for s in subs)} != {value}")
            node = {
                "id": f"ontario.{_slug(name)}",
                "name": name if not name.startswith("Interest") else "Interest on the debt",
                "_cat": mapping[label]["category"],
                "gross": r1(value),
                "net": None,
                "note": mapping[label]["notes"] or None,
                "source": {**ref, "locator": f"Table 3.10, {label}"},
            }
            if len(subs) > 1:
                node["children"] = subs
            ministries.append(node)
            pending = []
        else:
            pending.append((label, value))

    unused = set(mapping) - {f"{m['name']} (Total)" for m in ministries} - {
        k for k in mapping if k.startswith("Interest")
    }
    if unused:
        raise AssertionError(f"ontario.csv lines not found in Table 3.10: {sorted(unused)}")

    by_cat: dict[str, list[dict]] = defaultdict(list)
    for m in ministries:
        by_cat[m.pop("_cat")].append(m)
    children = []
    for cat, kids in by_cat.items():
        kids.sort(key=lambda k: -k["gross"])
        children.append(
            {
                "id": f"ontario.{cat}",
                "name": CATEGORY_NAMES[cat],
                "category": cat,
                "gross": r1(sum(k["gross"] for k in kids)),
                "net": None,
                "originalLines": [k["name"] for k in kids],
                "children": kids,
            }
        )
    children.sort(key=lambda c: -c["gross"])
    total = r1(sum(c["gross"] for c in children))
    for official, what in ((table_total, "Table 3.10 total row"), (OFFICIAL_TOTAL, "Table 3.1 total expense")):
        if official is None or abs(total - official) > 0.001 * official:
            raise AssertionError(f"Ontario tree total {total} != {what} {official}")
    return {
        "id": "ontario",
        "name": "Province of Ontario",
        "year": "2026-27",
        "basis": "total expense, budget plan (consolidated)",
        "gross": total,
        "net": None,
        "note": "Ministry totals from the 2026 Ontario Budget. Education includes colleges and universities and the teachers' pension plan here, so it is larger than the Budget's 'Education sector' figure.",
        "source": {**ref, "locator": "Table 3.10: Total Expense"},
        "children": children,
    }


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def main() -> int:
    write_json(CLEAN / "budget-ontario-2026-27.json", build())
    print("wrote data/clean/budget-ontario-2026-27.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
