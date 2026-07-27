#!/usr/bin/env python3
"""
track_rfis.py — Theo dõi & phân tích RFI từ register CSV.
                Track & analyze RFIs from a register CSV.

Tính days-open, nhóm aging, cờ quá hạn phản hồi, ball-in-court, ảnh hưởng
chi phí/tiến độ, và KPI thời gian phản hồi. Chỉ dùng thư viện chuẩn.
Compute days-open, aging buckets, overdue-response flags, ball-in-court,
cost/schedule impact and response-time KPIs. Stdlib only.

Usage:
    python track_rfis.py rfis.csv
    python track_rfis.py rfis.csv --as-of 2026-07-24 --csv out/rfi_register.csv
Exit: 0 = ok, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

CANON = ["id", "subject", "status", "ball_in_court", "discipline",
         "submitted_date", "response_due", "closed_date",
         "cost_impact", "schedule_impact"]
CLOSED_STATES = {"closed", "answered", "resolved", "void", "closed - answered"}
YES = {"yes", "y", "true", "1", "x", "có"}

# Alias cột không phân biệt hoa/thường (Procore / ACC / BIM360 / Excel).
ALIASES = {
    "id": "id", "rfi": "id", "rfi id": "id", "rfi number": "id",
    "number": "id", "no": "id", "ref": "id",
    "subject": "subject", "title": "subject", "question": "subject",
    "description": "subject", "name": "subject",
    "status": "status", "state": "status",
    "ball in court": "ball_in_court", "ball-in-court": "ball_in_court",
    "bic": "ball_in_court", "assigned to": "ball_in_court",
    "responsible": "ball_in_court", "court": "ball_in_court", "held by": "ball_in_court",
    "discipline": "discipline", "trade": "discipline", "type": "discipline", "category": "discipline",
    "submitted": "submitted_date", "submitted date": "submitted_date",
    "date submitted": "submitted_date", "created": "submitted_date",
    "created date": "submitted_date", "opened": "submitted_date",
    "response due": "response_due", "due": "response_due", "due date": "response_due",
    "date required": "response_due", "answer due": "response_due", "required by": "response_due",
    "closed": "closed_date", "closed date": "closed_date", "date closed": "closed_date",
    "answered date": "closed_date", "response date": "closed_date",
    "cost impact": "cost_impact", "cost": "cost_impact",
    "schedule impact": "schedule_impact", "schedule": "schedule_impact", "time impact": "schedule_impact",
}

DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%d-%b-%Y", "%m/%d/%y")
AGING_ORDER = {"0-7": 0, "8-14": 1, "15-30": 2, "31+": 3, "(no date)": 4}


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


def read_rfis(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return [normalize_row(r) for r in csv.DictReader(fh)]


def is_closed(r: dict) -> bool:
    return r["status"].strip().lower() in CLOSED_STATES or parse_date(r["closed_date"]) is not None


def is_yes(v: str) -> bool:
    return v.strip().lower() in YES


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
        sub = parse_date(r["submitted_date"])
        closed = parse_date(r["closed_date"])
        due = parse_date(r["response_due"])
        r["_closed"] = is_closed(r)
        r["days_open"] = (closed or as_of) - sub if sub else None
        r["days_open"] = r["days_open"].days if r["days_open"] is not None else None
        r["overdue"] = "yes" if (due and due < as_of and not r["_closed"]) else "no"
        r["bucket"] = "closed" if r["_closed"] else aging_bucket(r["days_open"])
        r["_response_days"] = (closed - sub).days if (closed and sub) else None
    return rows


def summarize(rows: list[dict], as_of: date) -> str:
    open_rows = [r for r in rows if not r["_closed"]]
    closed_rows = [r for r in rows if r["_closed"]]
    L = [f"RFI tracker — mốc so hạn / as of: {as_of.isoformat()}",
         f"Tổng / Total: {len(rows)}  |  đang mở / open: {len(open_rows)}  "
         f"|  đã đóng / closed: {len(closed_rows)}", ""]

    L.append("Theo trạng thái / By status:")
    for val, n in Counter(r["status"] or "(blank)" for r in rows).most_common():
        L.append(f"  {n:4}  {val}")
    L.append("")

    L.append("Ball-in-court (đang mở / open only):")
    for val, n in Counter(r["ball_in_court"] or "(blank)" for r in open_rows).most_common():
        L.append(f"  {n:4}  {val}")
    L.append("")

    L.append("Aging — số ngày mở / days open (đang mở / open only):")
    for val, n in sorted(Counter(r["bucket"] for r in open_rows).items(),
                         key=lambda kv: AGING_ORDER.get(kv[0], 9)):
        L.append(f"  {n:4}  {val}")
    L.append("")

    overdue = [r for r in open_rows if r["overdue"] == "yes"]
    L.append(f"Quá hạn phản hồi / Overdue response: {len(overdue)}")
    for r in sorted(overdue, key=lambda r: r["days_open"] or 0, reverse=True):
        L.append(f"  - {r['id']} {r['subject']}  (due {r['response_due']}, "
                 f"{r['days_open']}d open, BIC {r['ball_in_court'] or '?'})")
    L.append("")

    cost = sum(1 for r in rows if is_yes(r["cost_impact"]))
    sched = sum(1 for r in rows if is_yes(r["schedule_impact"]))
    L.append(f"Ảnh hưởng chi phí / Cost impact: {cost}   "
             f"|   tiến độ / schedule impact: {sched}")

    resp = [r["_response_days"] for r in closed_rows if r["_response_days"] is not None]
    if resp:
        L.append(f"Thời gian phản hồi (đã đóng) / Response time (closed): "
                 f"tb/avg {statistics.mean(resp):.1f}d, "
                 f"trung vị/median {statistics.median(resp):.0f}d, max {max(resp)}d")
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
    ap = argparse.ArgumentParser(description="Track & analyze RFIs from a register CSV.")
    ap.add_argument("csv", help="File CSV RFI register")
    ap.add_argument("--as-of", help="Mốc so hạn YYYY-MM-DD (mặc định hôm nay)")
    ap.add_argument("--csv", dest="out_csv", help="Xuất register CSV có cột tính toán")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2
    as_of = parse_date(args.as_of) or date.today()

    rows = enrich(read_rfis(path), as_of)
    print(summarize(rows, as_of))
    if args.out_csv:
        write_csv(rows, Path(args.out_csv))
        print(f"\nĐã ghi register / wrote register: {args.out_csv} ({len(rows)} dòng)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
