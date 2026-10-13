"""Shared paths, constants and helpers for the pipeline."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
CLEAN = DATA / "clean"
FACTS = DATA / "facts"
MAPPINGS = DATA / "mappings"
SOURCES_JSON = DATA / "sources.json"

AS_OF = "2026-10-12"

# Shared categories (docs/data-contract.md)
CATEGORIES = [
    "transit",
    "police-justice",
    "fire-paramedics",
    "housing-shelter",
    "social-services",
    "health",
    "education",
    "parks-rec-culture",
    "infrastructure",
    "government-debt",
    "other",
]
CATEGORY_NAMES = {
    "transit": "Transit",
    "police-justice": "Police & Justice",
    "fire-paramedics": "Fire & Paramedics",
    "housing-shelter": "Housing & Shelter",
    "social-services": "Social Services",
    "health": "Health",
    "education": "Education",
    "parks-rec-culture": "Parks, Recreation & Culture",
    "infrastructure": "Infrastructure (roads, water, waste)",
    "government-debt": "Government & Debt",
    "other": "Other",
}

SCARBOROUGH_WARDS = [20, 21, 22, 23, 24, 25]

BUDGET_SUMMARY_URL = (
    "https://www.toronto.ca/wp-content/uploads/2026/05/"
    "8f04-2026-City-of-Toronto-Budget-Summary.pdf"
)
BUDGET_SUMMARY_TITLE = "2026 City of Toronto Budget Summary"

ONTARIO_BUDGET_CH3_URL = "https://budget.ontario.ca/2026/chapter-3.html"
ONTARIO_BUDGET_TITLE = "2026 Ontario Budget, Chapter 3"


def load_sources() -> list[dict]:
    if SOURCES_JSON.exists():
        return json.loads(SOURCES_JSON.read_text())
    return []


def source(source_id: str) -> dict:
    for s in load_sources():
        if s["id"] == source_id:
            return s
    raise KeyError(f"source {source_id!r} not in data/sources.json; run fetch first")


def raw_path(source_id: str) -> Path:
    return ROOT / source(source_id)["file"]


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def r1(x: float) -> float:
    """Round $M to one decimal."""
    return round(float(x) + 0.0, 1)


def r3(x: float) -> float:
    return round(float(x) + 0.0, 3)
