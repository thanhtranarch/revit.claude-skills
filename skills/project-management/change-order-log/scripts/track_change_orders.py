#!/usr/bin/env python3
"""
track_change_orders.py — Theo dõi change order / variation với ảnh hưởng chi phí
                         & tiến độ. Track change orders (variations) with cost &
                         schedule impact and running totals.

Chỉ dùng thư viện chuẩn. / Stdlib only.

Usage:
    python track_change_orders.py changes.csv
    python track_change_orders.py changes.csv --as-of 2026-07-24 --csv out/co_register.csv
Exit: 0 = ok, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

CANON = ["id", "title", "status", "discipline", "initiator",
         "submitted_date", "due_date", "approved_date",
         "cost_amount", "schedule_days", "reason"]
APPROVED = {"approved", "approved as noted", "accepted"}
REJECTED = {"rejected", "declined", "void", "withdrawn"}

ALIASES = {
    "id": "id", "co": "id", "co no": "id", "co number": "id", "change order": "id",
    "variation": "id", "number": "id", "no": "id", "ref": "id", "pco": "id",
    "title": "title", "description": "title", "subject": "title", "name": "title",
    "status": "status", "state": "status", "disposition": "status",
    "discipline": "discipline", "trade": "discipline", "type": "discipline", "category": "discipline",
    "initiator": "initiator", "originator": "initiator", "raised by": "initiator",
    "requested by": "initiator", "source": "initiator",
    "submitted": "submitted_date", "submitted date": "submitted_date",
    "date submitted": "submitted_date", "created": "submitted_date", "raised": "submitted_date",
    "due": "due_date", "due date": "due_date", "response due": "due_date", "required by": "due_date",
    "approved": "approved_date", "approved date": "approved_date", "date approved": "approved_date",
    "decision date": "approved_date", "closed date": "approved_date",
    "cost": "cost_amount", "cost amount": "cost_amount", "amount": "cost_amount",
    "value": "cost_amount", "cost impact": "cost_amount", "$": "cost_amount",
    "schedule days": "schedule_days", "time impact": "schedule_days",
    "schedule impact": "schedule_days", "days": "schedule_days", "eot": "schedule_days",
    "reason": "reason", "justification": "reason", "cause": "reason",
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


def parse_money(s: str) -> float:
    s = (s or "").strip()
    if not s:
        return 0.0
    neg = s.startswith("(") and s.endswith(")")
    cleaned = re.sub(r"[^0-9.\-]", "", s)
    if cleaned in ("", "-", ".", "-.", "--"):
        return 0.0
    try:
        val = float(cleaned)
    except ValueError:
        return 0.0
    return -val if neg else val


def parse_days(s: str) -> int:
    m = re.search(r"-?\d+", s or "")
    return int(m.group()) if m else 0


def normalize_row(row: dict) -> dict:
    out = {c: "" for c in CANON}
    for k, v in row.items():
        if k is None:
            continue
        canon = ALIASES.get(k.strip().lower())
        if canon and not out[canon]:
            out[canon] = (v or "").strip()
    return out


def read_changes(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return [normalize_row(r) for r in csv.DictReader(fh)]


def bucket(status: str) -> str:
    s = status.strip().lower()
    if s in APPROVED:
        return "approved"
    if s in REJECTED:
        return "rejected"
    return "pending"


def enrich(rows: list[dict], as_of: date) -> list[dict]:
    for r in rows:
        r["cost_value"] = parse_money(r["cost_amount"])
        r["sched_value"] = parse_days(r["schedule_days"])
        r["bucket"] = bucket(r["status"])
        sub = parse_date(r["submitted_date"])
        due = parse_date(r["due_date"])
        r["days_open"] = (as_of - sub).days if (sub and r["bucket"] == "pending") else None
        r["overdue"] = "yes" if (due and due < as_of and r["bucket"] == "pending") else "no"
    return rows


def money(v: float) -> str:
    return f"{v:,.0f}"


def summarize(rows: list[dict], as_of: date) -> str:
    pend = [r for r in rows if r["bucket"] == "pending"]
    appr = [r for r in rows if r["bucket"] == "approved"]
    rej = [r for r in rows if r["bucket"] == "rejected"]
    L = [f"Change order log — mốc so hạn / as of: {as_of.isoformat()}",
         f"Tổng / Total: {len(rows)}  |  chờ / pending: {len(pend)}  "
         f"|  duyệt / approved: {len(appr)}  |  từ chối / rejected: {len(rej)}", ""]

    L.append("Theo trạng thái / By status:")
    for val, n in Counter(r["status"] or "(blank)" for r in rows).most_common():
        L.append(f"  {n:4}  {val}")
    L.append("")

    L.append("Giá trị / Value (cost_amount):")
    L.append(f"  Đã gửi / Submitted (all): {money(sum(r['cost_value'] for r in rows))}")
    L.append(f"  Đã duyệt / Approved:      {money(sum(r['cost_value'] for r in appr))}")
    L.append(f"  Đang chờ / Pending:       {money(sum(r['cost_value'] for r in pend))}")
    L.append(f"  Bị từ chối / Rejected:    {money(sum(r['cost_value'] for r in rej))}")
    L.append(f"  Tiến độ được duyệt / Approved schedule days: "
             f"{sum(r['sched_value'] for r in appr)}")
    L.append("")

    by_disc: dict[str, float] = defaultdict(float)
    for r in rows:
        by_disc[r["discipline"] or "(blank)"] += r["cost_value"]
    L.append("Giá trị theo bộ môn / Value by discipline:")
    for val, amt in sorted(by_disc.items(), key=lambda kv: -kv[1]):
        L.append(f"  {money(amt):>14}  {val}")
    L.append("")

    overdue = [r for r in pend if r["overdue"] == "yes"]
    L.append(f"Quá hạn quyết định / Overdue decision: {len(overdue)}")
    for r in sorted(overdue, key=lambda r: r["days_open"] or 0, reverse=True):
        L.append(f"  - {r['id']} {r['title']}  (due {r['due_date']}, "
                 f"{r['days_open']}d, {money(r['cost_value'])})")
    return "\n".join(L)


def write_csv(rows: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = CANON + ["cost_value", "sched_value", "bucket", "days_open", "overdue"]
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Track change orders / variations.")
    ap.add_argument("csv", help="File CSV change-order register")
    ap.add_argument("--as-of", help="Mốc so hạn YYYY-MM-DD (mặc định hôm nay)")
    ap.add_argument("--csv", dest="out_csv", help="Xuất register CSV có cột tính toán")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2
    as_of = parse_date(args.as_of) or date.today()

    rows = enrich(read_changes(path), as_of)
    print(summarize(rows, as_of))
    if args.out_csv:
        write_csv(rows, Path(args.out_csv))
        print(f"\nĐã ghi register / wrote register: {args.out_csv} ({len(rows)} dòng)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
