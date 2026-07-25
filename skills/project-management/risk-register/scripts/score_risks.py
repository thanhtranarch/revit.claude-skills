#!/usr/bin/env python3
"""
score_risks.py — Chấm điểm & phân loại risk register (probability × impact).
                 Score & rate a project risk register (probability × impact).

Đổi probability/impact (1–5 hoặc Low/Medium/High…) thành điểm P×I, gán RAG
(đỏ/vàng/xanh), gom theo RAG/owner/category, và bắt review quá hạn. Chỉ dùng
thư viện chuẩn.

Usage:
    python score_risks.py risks.csv
    python score_risks.py risks.csv --as-of 2026-07-24 --csv out/risk_register.csv
Exit: 0 = ok, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

CANON = ["id", "description", "category", "owner", "probability", "impact",
         "status", "review_date", "mitigation"]
CLOSED_STATES = {"closed", "retired", "expired", "realised", "realized"}
LEVELS = {
    "very low": 1, "vl": 1, "1": 1,
    "low": 2, "l": 2, "2": 2, "minor": 2, "unlikely": 2,
    "medium": 3, "med": 3, "m": 3, "moderate": 3, "3": 3, "possible": 3,
    "high": 4, "h": 4, "4": 4, "major": 4, "likely": 4,
    "very high": 5, "vh": 5, "5": 5, "critical": 5, "severe": 5, "almost certain": 5,
}
ALIASES = {
    "id": "id", "risk id": "id", "risk": "id", "ref": "id", "no": "id", "number": "id",
    "description": "description", "risk description": "description", "title": "description",
    "desc": "description", "event": "description", "name": "description",
    "category": "category", "type": "category", "area": "category", "risk category": "category",
    "owner": "owner", "risk owner": "owner", "assigned to": "owner", "responsible": "owner",
    "probability": "probability", "likelihood": "probability", "prob": "probability", "p": "probability",
    "impact": "impact", "consequence": "impact", "severity": "impact", "i": "impact",
    "status": "status", "state": "status",
    "review date": "review_date", "review": "review_date", "next review": "review_date",
    "due": "review_date", "review by": "review_date",
    "mitigation": "mitigation", "response": "mitigation", "action": "mitigation",
    "treatment": "mitigation", "control": "mitigation",
}
DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%d-%b-%Y", "%m/%d/%y")


def parse_date(s: str):
    s = (s or "").strip()
    if not s:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def level(s: str):
    s = (s or "").strip().lower()
    if not s:
        return None
    if s in LEVELS:
        return LEVELS[s]
    try:
        n = int(float(s))
        return max(1, min(5, n))
    except ValueError:
        return None


def rag(score):
    if score is None:
        return "?"
    if score >= 15:
        return "RED"
    if score >= 8:
        return "AMBER"
    return "GREEN"


def normalize_row(row: dict) -> dict:
    out = {c: "" for c in CANON}
    for k, v in row.items():
        if k is None:
            continue
        canon = ALIASES.get(k.strip().lower())
        if canon and not out[canon]:
            out[canon] = (v or "").strip()
    return out


def read_risks(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return [normalize_row(r) for r in csv.DictReader(fh)]


def enrich(rows: list[dict], as_of: date) -> list[dict]:
    for r in rows:
        p, i = level(r["probability"]), level(r["impact"])
        r["_p"], r["_i"] = p, i
        r["score"] = p * i if (p and i) else None
        r["rag"] = rag(r["score"])
        r["_closed"] = r["status"].strip().lower() in CLOSED_STATES
        rev = parse_date(r["review_date"])
        r["review_overdue"] = "yes" if (rev and rev < as_of and not r["_closed"]) else "no"
    return rows


def summarize(rows: list[dict], as_of: date) -> str:
    open_rows = [r for r in rows if not r["_closed"]]
    L = [f"Risk register — mốc so hạn / as of: {as_of.isoformat()}",
         f"Tổng / Total: {len(rows)}  |  đang mở / open: {len(open_rows)}  "
         f"|  đã đóng / closed: {len(rows) - len(open_rows)}", ""]

    order = {"RED": 0, "AMBER": 1, "GREEN": 2, "?": 3}
    L.append("Theo RAG (đang mở / open):")
    for val, n in sorted(Counter(r["rag"] for r in open_rows).items(),
                         key=lambda kv: order.get(kv[0], 9)):
        L.append(f"  {n:4}  {val}")
    L.append("")

    for label, field in (("chủ rủi ro / owner", "owner"), ("nhóm / category", "category")):
        if any(r[field] for r in rows):
            L.append(f"Theo {label} (đang mở / open):")
            for val, n in Counter(r[field] or "(blank)" for r in open_rows).most_common():
                L.append(f"  {n:4}  {val}")
            L.append("")

    overdue = [r for r in open_rows if r["review_overdue"] == "yes"]
    L.append(f"Review quá hạn / Overdue review: {len(overdue)}")
    for r in overdue:
        L.append(f"  - {r['id']} {r['description']}  (review {r['review_date']}, {r['owner'] or '?'})")
    L.append("")

    scored = [r for r in open_rows if r["score"] is not None]
    L.append("Top rủi ro (điểm P×I cao nhất, đang mở) / Top open risks:")
    for r in sorted(scored, key=lambda r: r["score"], reverse=True)[:5]:
        L.append(f"  [{r['rag']:5} {r['score']:2}]  {r['id']} {r['description']}  "
                 f"(P{r['_p']}×I{r['_i']}, {r['owner'] or '?'})")
    return "\n".join(L)


def write_csv(rows: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = CANON + ["score", "rag", "review_overdue"]
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Score & rate a project risk register.")
    ap.add_argument("csv", help="File CSV risk register")
    ap.add_argument("--as-of", help="Mốc so hạn YYYY-MM-DD (mặc định hôm nay)")
    ap.add_argument("--csv", dest="out_csv", help="Xuất register CSV có score/rag")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2
    as_of = parse_date(args.as_of) or date.today()

    rows = enrich(read_risks(path), as_of)
    print(summarize(rows, as_of))
    if args.out_csv:
        write_csv(rows, Path(args.out_csv))
        print(f"\nĐã ghi register / wrote register: {args.out_csv} ({len(rows)} dòng)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
