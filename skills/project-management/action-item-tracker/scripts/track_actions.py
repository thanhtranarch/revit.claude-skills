#!/usr/bin/env python3
"""
track_actions.py — Theo dõi action item (họp/coordination) từ register CSV.
                   Track meeting / coordination action items from a register CSV.

Tính days-open, aging, quá hạn; gom theo owner / cuộc họp / mức ưu tiên.
Chỉ dùng thư viện chuẩn. / Stdlib only.

Usage:
    python track_actions.py actions.csv
    python track_actions.py actions.csv --as-of 2026-07-24 --owner "J. Tran" --csv out/actions.csv
Exit: 0 = ok, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

CANON = ["id", "action", "owner", "status", "meeting", "priority",
         "raised_date", "due_date", "closed_date"]
CLOSED_STATES = {"closed", "done", "complete", "completed", "resolved", "cancelled", "canceled"}
AGING_ORDER = {"0-7": 0, "8-14": 1, "15-30": 2, "31+": 3, "(no date)": 4}

ALIASES = {
    "id": "id", "item": "id", "action id": "id", "no": "id", "number": "id", "ref": "id", "#": "id",
    "action": "action", "action item": "action", "task": "action",
    "description": "action", "title": "action", "detail": "action", "details": "action",
    "owner": "owner", "assignee": "owner", "assigned to": "owner",
    "responsible": "owner", "who": "owner", "by whom": "owner",
    "status": "status", "state": "status",
    "meeting": "meeting", "meeting id": "meeting", "source": "meeting",
    "meeting date": "meeting", "minutes": "meeting", "topic": "meeting",
    "priority": "priority", "importance": "priority", "severity": "priority",
    "raised": "raised_date", "raised date": "raised_date", "date raised": "raised_date",
    "created": "raised_date", "opened": "raised_date", "date": "raised_date",
    "due": "due_date", "due date": "due_date", "target": "due_date",
    "target date": "due_date", "deadline": "due_date", "by when": "due_date",
    "closed": "closed_date", "closed date": "closed_date",
    "completed date": "closed_date", "date closed": "closed_date", "done date": "closed_date",
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


def read_actions(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return [normalize_row(r) for r in csv.DictReader(fh)]


def is_closed(r: dict) -> bool:
    return r["status"].strip().lower() in CLOSED_STATES or parse_date(r["closed_date"]) is not None


def aging_bucket(days) -> str:
    if days is None:
        return "(no date)"
    if days <= 7:
        return "0-7"
    if days <= 14:
        return "8-14"
    if days <= 30:
        return "15-30"
    return "31+"


def enrich(rows: list[dict], as_of: date) -> list[dict]:
    for r in rows:
        raised = parse_date(r["raised_date"])
        closed = parse_date(r["closed_date"])
        due = parse_date(r["due_date"])
        r["_closed"] = is_closed(r)
        r["days_open"] = ((closed or as_of) - raised).days if raised else None
        r["overdue"] = "yes" if (due and due < as_of and not r["_closed"]) else "no"
        r["bucket"] = "closed" if r["_closed"] else aging_bucket(r["days_open"])
    return rows


def summarize(rows: list[dict], as_of: date) -> str:
    open_rows = [r for r in rows if not r["_closed"]]
    closed_rows = [r for r in rows if r["_closed"]]
    L = [f"Action items — mốc so hạn / as of: {as_of.isoformat()}",
         f"Tổng / Total: {len(rows)}  |  đang mở / open: {len(open_rows)}  "
         f"|  đã đóng / closed: {len(closed_rows)}", ""]

    L.append("Theo người phụ trách / By owner (đang mở / open):")
    for val, n in Counter(r["owner"] or "(unassigned)" for r in open_rows).most_common():
        L.append(f"  {n:4}  {val}")
    L.append("")

    if any(r["meeting"] for r in rows):
        L.append("Theo cuộc họp / By meeting (đang mở / open):")
        for val, n in Counter(r["meeting"] or "(none)" for r in open_rows).most_common():
            L.append(f"  {n:4}  {val}")
        L.append("")

    if any(r["priority"] for r in rows):
        L.append("Theo ưu tiên / By priority (đang mở / open):")
        for val, n in Counter(r["priority"] or "(none)" for r in open_rows).most_common():
            L.append(f"  {n:4}  {val}")
        L.append("")

    L.append("Aging — số ngày mở / days open (đang mở / open):")
    for val, n in sorted(Counter(r["bucket"] for r in open_rows).items(),
                         key=lambda kv: AGING_ORDER.get(kv[0], 9)):
        L.append(f"  {n:4}  {val}")
    L.append("")

    overdue = [r for r in open_rows if r["overdue"] == "yes"]
    L.append(f"Quá hạn / Overdue: {len(overdue)}")
    for r in sorted(overdue, key=lambda r: r["days_open"] or 0, reverse=True):
        L.append(f"  - {r['id']} {r['action']}  (due {r['due_date']}, "
                 f"{r['days_open']}d open, {r['owner'] or 'unassigned'})")
    return "\n".join(L)


def write_csv(rows: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = CANON + ["days_open", "overdue", "bucket"]
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Track meeting/coordination action items.")
    ap.add_argument("csv", help="File CSV action-item register")
    ap.add_argument("--as-of", help="Mốc so hạn YYYY-MM-DD (mặc định hôm nay)")
    ap.add_argument("--owner", help="Chỉ hiện action của một owner (lọc)")
    ap.add_argument("--csv", dest="out_csv", help="Xuất register CSV có cột tính toán")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2
    as_of = parse_date(args.as_of) or date.today()

    rows = enrich(read_actions(path), as_of)
    if args.owner:
        needle = args.owner.strip().lower()
        rows = [r for r in rows if needle in r["owner"].lower()]
        if not rows:
            print(f"Không có action nào cho owner khớp '{args.owner}'.")
            return 0
    print(summarize(rows, as_of))
    if args.out_csv:
        write_csv(rows, Path(args.out_csv))
        print(f"\nĐã ghi register / wrote register: {args.out_csv} ({len(rows)} dòng)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
