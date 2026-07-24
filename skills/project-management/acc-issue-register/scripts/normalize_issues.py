#!/usr/bin/env python3
"""
normalize_issues.py — Chuẩn hoá & tóm tắt CSV issue của ACC/BIM360.
                      Normalize & summarize an ACC/BIM360 issues CSV.

Chỉ dùng thư viện chuẩn. / Stdlib only.

Usage:
    python normalize_issues.py export.csv
    python normalize_issues.py export.csv --csv register.csv --as-of 2026-07-24
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

CANON = ["id", "title", "status", "assignee", "discipline", "due_date", "location"]
CLOSED_STATES = {"closed", "resolved", "answered", "not an issue", "void"}

ALIASES = {
    "id": "id", "issue id": "id", "no": "id", "number": "id",
    "title": "title", "subject": "title", "name": "title",
    "status": "status", "state": "status",
    "assignee": "assignee", "assigned to": "assignee", "owner": "assignee", "responsible": "assignee",
    "discipline": "discipline", "trade": "discipline", "category": "discipline", "type": "discipline",
    "due date": "due_date", "due": "due_date", "deadline": "due_date",
    "location": "location", "sheet": "location", "space": "location", "area": "location",
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


def normalize_row(row: dict) -> dict:
    out = {c: "" for c in CANON}
    for k, v in row.items():
        if k is None:
            continue
        canon = ALIASES.get(k.strip().lower())
        if canon and not out[canon]:
            out[canon] = (v or "").strip()
    return out


def read_issues(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return [normalize_row(r) for r in csv.DictReader(fh)]


def flag_overdue(rows: list[dict], as_of: date) -> None:
    for r in rows:
        due = parse_date(r["due_date"])
        closed = r["status"].strip().lower() in CLOSED_STATES
        r["overdue"] = "yes" if (due and due < as_of and not closed) else "no"


def summarize(rows: list[dict], as_of: date) -> str:
    lines = [f"Tổng issue / Total: {len(rows)}", f"Mốc so hạn / As of: {as_of.isoformat()}", ""]
    for label, field in (("trạng thái / status", "status"),
                         ("người phụ trách / assignee", "assignee"),
                         ("bộ môn / discipline", "discipline")):
        lines.append(f"Theo {label}:")
        for val, n in Counter(r[field] or "(blank)" for r in rows).most_common():
            lines.append(f"  {n:4}  {val}")
        lines.append("")
    overdue = [r for r in rows if r.get("overdue") == "yes"]
    lines.append(f"Quá hạn / Overdue: {len(overdue)}")
    for r in overdue:
        lines.append(f"  - {r['id']} {r['title']} (due {r['due_date']}, {r['assignee']})")
    return "\n".join(lines)


def write_csv(rows: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = CANON + ["overdue"]
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Normalize ACC/BIM360 issues CSV.")
    ap.add_argument("csv", help="File CSV export")
    ap.add_argument("--csv", dest="out_csv", help="Xuất register CSV")
    ap.add_argument("--as-of", help="Mốc so hạn YYYY-MM-DD (mặc định hôm nay)")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2
    as_of = parse_date(args.as_of) or date.today()

    rows = read_issues(path)
    flag_overdue(rows, as_of)
    print(summarize(rows, as_of))
    if args.out_csv:
        write_csv(rows, Path(args.out_csv))
        print(f"\nĐã ghi register: {args.out_csv} ({len(rows)} dòng)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
