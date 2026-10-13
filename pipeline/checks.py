"""Reconciliation checks (spec §8). Exit non-zero on any failure.

1. Budget trees: every node's gross equals the sum of its children (within 0.5 $M),
   and categories are from the shared list.
2. Pipeline-checked facts: values in data/facts/*.yaml are re-derived from the raw
   files and must match.

Usage:
    uv run python -m pipeline.checks
"""
from __future__ import annotations

import json
import sys

import yaml

from . import budget_summary
from .common import CATEGORIES, CLEAN, FACTS, SCARBOROUGH_WARDS

TREE_TOL = 0.5


def check_tree(node: dict, path: str, errors: list[str]) -> None:
    kids = node.get("children") or []
    if "category" in node and node["category"] not in CATEGORIES:
        errors.append(f"{path}: unknown category {node['category']!r}")
    if kids:
        s = sum(k["gross"] for k in kids)
        if abs(s - node["gross"]) > TREE_TOL:
            errors.append(f"{path}: gross {node['gross']} != sum of children {s:.1f}")
        for k in kids:
            check_tree(k, f"{path} > {k['name']}", errors)


def derived_facts() -> dict[str, float]:
    """Fact id -> value re-computed from the pipeline's sources."""
    bs = budget_summary.get()
    wards = json.loads((CLEAN / "wards.json").read_text())
    scar = [w for w in wards["wards"] if w["ward"] in SCARBOROUGH_WARDS]
    fig1 = {i["label"]: i["value"] for i in bs["figure1"]["items"]}
    g = bs["glance"]
    tor = json.loads((CLEAN / "budget-toronto-2026.json").read_text())
    transport = next(k for c in tor["children"] for k in c.get("children") or [] if k["id"] == "toronto.transportation-services")
    finch = sum(p["amount10yr"] for w in scar for p in w["topProjects"] if p["name"] == "4610 Finch Ave East")
    return {
        "toronto.operating.2026.gross": sum(fig1.values()),
        "toronto.revenue.2026.property-tax": fig1["Property Tax"],
        "toronto.revenue.2026.fed-prov": fig1["Federal / Provincial Funding"],
        "toronto.property-tax.2026.avg-bill": bs["tax"]["avgBill"],
        "toronto.property-tax.2026.increase": bs["tax"]["rateIncreasePct"],
        "toronto.ttc.2026.gross": g["Toronto Transit Commission"]["gross"],
        "toronto.ttc.2026.net": g["Toronto Transit Commission"]["net"],
        "toronto.police.2026.gross": g["Toronto Police Service"]["gross"],
        "toronto.police.2026.net": g["Toronto Police Service"]["net"],
        "toronto.shelter.2026.gross": g["Toronto Shelter and Support Services"]["gross"],
        "toronto.transportation.2026.gross": transport["gross"],
        "toronto.capital.2026-2035.total": bs["capital"]["capital10yrGross"],
        "scarborough.population.2021": sum(w["population"] for w in scar),
        "scarborough.capital.2026-2035.ward-tagged": sum(w["capital10yr"] for w in scar),
        "scarborough.capital.finch-ltc": finch,
        "scarborough.capital.city-wide-share": wards["cityWide"]["share"] * 100,
    }


def load_facts() -> dict:
    facts = {}
    for f in sorted(FACTS.glob("*.yaml")):
        facts.update(yaml.safe_load(f.read_text()) or {})
    return facts


def main() -> int:
    errors: list[str] = []
    for f in sorted(CLEAN.glob("budget-*.json")):
        tree = json.loads(f.read_text())
        check_tree(tree, f.name, errors)

    facts = load_facts()
    for fid, value in derived_facts().items():
        if fid not in facts:
            errors.append(f"fact {fid} is derived by the pipeline but missing from data/facts")
            continue
        stated = facts[fid]["value"]
        # Facts are rounded for display: allow half a unit of the stated precision, min 0.5 $M.
        tol = max(0.5, abs(value) * 0.0005)
        if abs(float(stated) - value) > tol:
            errors.append(f"fact {fid} = {stated}, but the pipeline derives {value:.2f}")

    if errors:
        print(f"✗ {len(errors)} check(s) failed:", *errors, sep="\n  - ", file=sys.stderr)
        return 1
    print(f"✓ checks passed: trees balanced, {len(derived_facts())} facts match the pipeline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
