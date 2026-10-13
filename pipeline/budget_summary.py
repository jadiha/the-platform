"""Extract figures from the 2026 City of Toronto Budget Summary PDF with pdfplumber.

Every value carries the PDF page number it came from. Pages are located by
searching for their headings, not hard-coded, so a re-issued PDF with shifted
pagination still parses (or fails loudly).

Outputs (in-memory dict, also cached to data/interim/budget-summary-2026.json):
  appendix: per-program 2025/2026 gross, revenue and net ($000s) from
            Appendix 1.1.1 (net), 1.1.2 (gross) and 1.1.3 (revenues)
  table1, table2, figure1, figure2, tax, programPages: headline figures
"""
from __future__ import annotations

import json
import re
from functools import lru_cache

import pdfplumber

from .common import DATA, r1, raw_path, source

SOURCE_ID = "toronto-budget-summary-2026"
CACHE = DATA / "interim" / "budget-summary-2026.json"
PARSER_VERSION = 2  # bump when extraction logic changes, to invalidate the cache

# Numeric columns of Appendix 1.1.x tables, left to right:
# 2025 Budget, 2025 Projection, 2026 Total Budget, 2027 Plan, 2028 Plan, Incr/(Dcr), %
# Their right edges (x1) are found per page, since re-issued PDFs shift them.
APPENDIX_COLS = ["b2025", "p2025", "b2026", "o2027", "o2028", "chg", "pct"]
X_TOL = 7
LABEL_MAX_X0 = 240

NUM_RE = re.compile(r"^\(?-?[\d,]*\.?\d+%?\)?$|^n/a$")


def _num(tok: str) -> float | None:
    tok = tok.strip()
    if tok == "n/a":
        return None
    neg = tok.startswith("(") and tok.endswith(")")
    tok = tok.strip("()").replace(",", "").replace("%", "")
    v = float(tok)
    return -v if neg else v


def norm_label(s: str) -> str:
    s = s.replace("–", "-").replace("’", "'")
    s = re.sub(r"[-\s]+", " ", s).strip().lower()
    return s


def _lines(page) -> list[list[dict]]:
    words = page.extract_words(keep_blank_chars=False, use_text_flow=False)
    words.sort(key=lambda w: (round(w["top"]), w["x0"]))
    lines: list[list[dict]] = []
    for w in words:
        if lines and abs(lines[-1][0]["top"] - w["top"]) < 2.5:
            lines[-1].append(w)
        else:
            lines.append([w])
    for ln in lines:
        ln.sort(key=lambda w: w["x0"])
    return lines


def parse_appendix_page(page, page_no: int) -> list[dict]:
    """Return rows: {label, kind: header|row, values{col: $000s}, page}."""
    # Drop the running footer ("2026 City of Toronto Budget Summary 264 Return to ToC").
    lines = [ln for ln in _lines(page) if not any(w["text"] == "ToC" for w in ln)]
    edges = sorted(
        w["x1"] for ln in lines for w in ln
        if ln[0]["top"] >= 115 and w["x0"] >= LABEL_MAX_X0 and NUM_RE.match(w["text"])
    )
    clusters: list[list[float]] = []
    for x in edges:
        if clusters and x - clusters[-1][-1] <= X_TOL:
            clusters[-1].append(x)
        else:
            clusters.append([x])
    if len(clusters) != len(APPENDIX_COLS):
        raise ValueError(f"p.{page_no}: found {len(clusters)} numeric columns, expected {len(APPENDIX_COLS)}")
    col_x1 = [max(c) for c in clusters]
    rows = []
    for ln in lines:
        if ln[0]["top"] < 115:  # page heading and column headings
            continue
        label_words = [w for w in ln if not (NUM_RE.match(w["text"]) and w["x0"] >= LABEL_MAX_X0)]
        nums = [w for w in ln if NUM_RE.match(w["text"]) and w["x0"] >= LABEL_MAX_X0]
        if any(w["x0"] >= LABEL_MAX_X0 for w in label_words):
            continue  # a heading line with words in the numeric area
        label = " ".join(w["text"] for w in label_words).strip()
        if not label:
            continue
        if label.startswith("2026 City of Toronto Budget Summary") or label.startswith("Return to"):
            continue
        values: dict[str, float | None] = {}
        for w in nums:
            idx = min(range(len(col_x1)), key=lambda i: abs(col_x1[i] - w["x1"]))
            if abs(col_x1[idx] - w["x1"]) > X_TOL:
                raise ValueError(f"p.{page_no}: token {w['text']!r} at x1={w['x1']:.0f} fits no column ({label})")
            col = APPENDIX_COLS[idx]
            if col in values:
                raise ValueError(f"p.{page_no}: two tokens in column {col} ({label})")
            values[col] = _num(w["text"])
        rows.append({"label": label, "kind": "row" if values else "header", "values": values, "page": page_no})
    return rows


def structure_appendix(rows: list[dict]) -> dict:
    """Turn the flat rows of one appendix (two pages) into labelled programs.

    Returns {key: {label, section, group, page, values}} where key is
    "<section>|<group>|<label>" normalised. section is one of
    city-operations, agencies, corporate, non-levy. group is the cluster
    (e.g. "community and emergency services") or corporate sub-group.
    """
    out: dict[str, dict] = {}
    section = "city-operations"
    group = None
    corporate_groups = {
        "capital & corporate financing": "capital & corporate financing",
        "non program expenditures": "non program expenditures",
        "non program revenues": "non program revenues",
    }
    for r in rows:
        lab = norm_label(r["label"])
        if r["kind"] == "header":
            if lab == "agencies":
                section, group = "agencies", None
            elif lab == "corporate accounts":
                section, group = "corporate", None
            elif lab == "non levy operation" or lab.startswith("non levy operation"):
                section, group = "non-levy", None
            elif section == "corporate" and lab in corporate_groups:
                group = corporate_groups[lab]
            elif section == "city-operations":
                group = lab
            continue
        if lab.startswith("sub total") or lab.startswith("total") or lab.startswith("opening tax"):
            if lab.startswith("total") and section == "city-operations" and "city operations" in lab:
                out[f"total|{lab}"] = {**r, "section": "total", "group": None}
            else:
                out[f"total|{lab}"] = {**r, "section": "total", "group": None}
            continue
        if lab in ("assessment growth", "property tax rate increase", "city building fund (cbf)",
                   "grouping capital levies (cbf and special scarborough transit levy)"):
            continue
        if section == "corporate" and lab in corporate_groups.values():
            out[f"corporate-subtotal|{lab}"] = {**r, "section": "corporate", "group": None, "subtotal": True}
            group = None
            continue
        if section == "corporate" and lab in ("arena boards of management", "association of community centres"):
            group = None
        key = f"{section}|{group or ''}|{lab}"
        if key in out:
            raise ValueError(f"duplicate appendix row {key}")
        out[key] = {**r, "section": section, "group": group}
    return out


def _find_pages(pdf, pattern: str) -> list[int]:
    hits = []
    for i, p in enumerate(pdf.pages, 1):
        t = p.extract_text() or ""
        if re.search(pattern, t):
            hits.append(i)
    return hits


def _money(s: str) -> float:
    return float(s.replace(",", "").replace("$", ""))


def extract() -> dict:
    path = raw_path(SOURCE_ID)
    sha = source(SOURCE_ID)["sha256"]
    if CACHE.exists():
        cached = json.loads(CACHE.read_text())
        if cached.get("sha256") == sha and cached.get("parser") == PARSER_VERSION:
            return cached

    pdf = pdfplumber.open(path)
    texts = {i: (p.extract_text() or "") for i, p in enumerate(pdf.pages, 1)}

    def pages_matching(pat: str) -> list[int]:
        return [i for i, t in texts.items() if re.search(pat, t)]

    def one_page(pat: str) -> int:
        hits = pages_matching(pat)
        if not hits:
            raise ValueError(f"no page matches {pat!r}")
        return hits[0]

    out: dict = {"sha256": sha, "parser": PARSER_VERSION, "pages": len(pdf.pages)}

    # ---- Table 1 / Table 2 (pp. 9-10) are drawn as skewed graphics and do not
    # extract as text, so the headline totals are taken from figures and
    # appendices that do extract cleanly, and cross-checked in checks.py:
    #   * operating gross = total of Figure 1 "Where the Money Comes From" (p.10)
    #     (a balanced budget: revenues = gross expenditures)
    #   * capital = Appendix 2.1.3 "Total Expenditure" row ($000s)
    out["table1"] = {"page": one_page(r"Table 1: 2026 Tax and Rate Operating Budget"),
                     "note": "Table 1 is a graphic; values are read from Figure 1 and Appendices 1.1.x / 2.1.3"}
    p = one_page(r"Tax and Rate Supported Budget . \$18\.9 Billion")
    t = texts[p]
    m = re.search(r"\$([\d.]+) billion gross / \$([\d.]+) billion net", t)
    out["overview"] = {"page": p, "taxSupportedGrossB": float(m.group(1)), "taxSupportedNetB": float(m.group(2))}
    m = re.search(r"Rate\s+(?:Tax\s+)?\$([\d.]+) billion", t)
    out["overview"]["rateSupportedB"] = float(m.group(1)) if m else None

    p = one_page(r"Appendix 2\.1\.3")
    m = re.search(r"^Total Expenditure ((?:[\d,]+ ?){12})$", texts[p], re.M)
    vals = [_money(v) for v in m.group(1).split()]
    # columns: carry-forward, 2026 ... 2035, 10-year total ($000s)
    out["capital"] = {
        "page": p,
        "locator": "Appendix 2.1.3, Total Expenditure row",
        "capital2026Gross": vals[1] / 1000,
        "capital10yrGross": vals[11] / 1000,
        "byYear000": vals[1:11],
    }

    # ---- Figure 1 (revenue) and Figure 2 (expenditure): "$4,935 26.2%" pairs
    p = one_page(r"Figure 1: 2026 Tax and Rate Operating Budget by Revenue")
    t = texts[p]
    items = re.findall(r"^([A-Z][A-Za-z &/]+?) \$([\d,]+) ([\d.]+)%", t, re.M)
    if len(items) != 9:
        raise ValueError(f"Figure 1 parse failed on p.{p}: {items}")
    out["figure1"] = {
        "page": p,
        "items": [{"label": lab.strip(), "value": _money(a), "pct": float(pc)} for lab, a, pc in items],
    }
    p = one_page(r"Figure 2: 2026 Tax and Rate Operating Budget by Expenditure")
    items = re.findall(r"^([A-Z][A-Za-z &]+?) \$([\d,]+) ([\d.]+)%", texts[p], re.M)
    if len(items) != 11:
        raise ValueError(f"Figure 2 parse failed on p.{p}: {items}")
    out["figure2"] = {
        "page": p,
        "items": [{"label": lab.strip(), "value": _money(a), "pct": float(pc)} for lab, a, pc in items],
    }

    # ---- Property tax impact
    p = one_page(r"residential tax rate is")
    t = re.sub(r"\s+", " ", texts[p])
    m = re.search(
        r"residential tax rate is ([\d.]+)%, of which ([\d.]+)% supports the 2026 Operating Budget and ([\d.]+)% "
        r"is allocated to the City Building Fund",
        t,
    )
    m2 = re.search(r"increase of \$([\d.]+) for the average assessed value", t)
    # The PDF splits digits with stray spaces here ("$4,2 52.").
    m3 = re.search(r"assessed at \$([\d.]+) thousand is \$([\d, ]+?)\.", t)
    out["tax"] = {
        "page": p,
        "rateIncreasePct": float(m.group(1)),
        "operatingPct": float(m.group(2)),
        "cityBuildingFundPct": float(m.group(3)),
        "avgHomeIncrease": float(m2.group(1)),
        "avgAssessment000": float(m3.group(1)),
        "avgBill": _money(m3.group(2).replace(" ", "")),
    }

    # ---- Program "Budget at a Glance" pages
    glance = {}
    for name in ("Toronto Police Service", "Toronto Shelter and Support Services",
                 "Toronto Transit Commission", "Toronto Fire Services", "Toronto Paramedic Services"):
        for p, t in texts.items():
            first = t.split("\n", 1)[0].strip()
            if not (first.endswith(name) and "Budget at a Glance" in t):
                continue
            # Anchor to line starts: the capital table shares lines with the operating table.
            m = re.search(r"^Gross Expenditures \$ ?([\d,]+\.\d+)", t, re.M)
            n = re.search(r"^Net Expenditures \$ ?([\d,]+\.\d+)", t, re.M)
            r = re.search(r"^Revenues \$ ?([\d,]+\.\d+)", t, re.M)
            if m and n and r:
                k = 1000 if "$Billion" in t else 1  # TTC reports in $ billions
                glance[name] = {"page": p, "gross": r1(_money(m.group(1)) * k), "net": r1(_money(n.group(1)) * k),
                                "revenues": r1(_money(r.group(1)) * k)}
                break
        if name not in glance:
            raise ValueError(f"Budget at a Glance page not found for {name}")
    out["glance"] = glance

    # ---- Appendices 1.1.1 (net), 1.1.2 (gross), 1.1.3 (revenues)
    app = {}
    for key, pat in {"net": r"Appendix 1\.1\.1", "gross": r"Appendix 1\.1\.2", "revenue": r"Appendix 1\.1\.3"}.items():
        pages = pages_matching(pat)
        if len(pages) != 2:
            raise ValueError(f"expected 2 pages for {pat}, got {pages}")
        rows = []
        for pg in pages:
            rows.extend(parse_appendix_page(pdf.pages[pg - 1], pg))
        app[key] = {"pages": pages, "rows": structure_appendix(rows)}
    out["appendix"] = app

    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out, indent=1))
    return out


@lru_cache(maxsize=1)
def get() -> dict:
    return extract()


if __name__ == "__main__":
    d = get()
    for k in ("table1", "overview", "capital", "figure1", "figure2", "tax", "glance"):
        print(k, json.dumps(d.get(k))[:600])
    for k, v in d["appendix"].items():
        print(k, v["pages"], len(v["rows"]))
        for key, r in v["rows"].items():
            print("   ", key, r["page"], r["values"].get("b2026"))
