#!/usr/bin/env python3
"""
build_submittal_log.py — Chuẩn hoá & theo dõi submittal register.
                         Normalize & track a construction submittal register.

Trạng thái vòng đời, ball-in-court, quá hạn, và thống kê chu kỳ review
(ngày nhận → ngày trả). Chỉ dùng thư viện chuẩn.
Lifecycle status, ball-in-court, overdue flags, and review-cycle stats.
Stdlib only.

Usage:
    python build_submittal_log.py submittals.csv
    python build_submittal_log.py submittals.csv --as-of 2026-07-24 --csv out/submittal_log.csv
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

CANON = ["id", "title", "spec_section", "status", "ball_in_court",
         "submitted_date", "due_date", "returned_date", "revision"]
COMPLETE = {"approved", "approved as noted", "closed", "no exceptions taken", "for record"}
RESUBMIT = {"revise and resubmit", "revise & resubmit", "rejected", "resubmit", "not approved"}

ALIASES = {
    "id": "id", "submittal": "id", "submittal no": "id", "submittal number": "id",
    "no": "id", "number": "id", "ref": "id", "package": "id",
    "title": "title", "description": "title", "subject": "title", "item": "title", "name": "title",
    "spec": "spec_section", "spec section": "spec_section", "section": "spec_section",
    "specification": "spec_section", "spec no": "spec_section",
    "status": "status", "state": "status", "disposition": "status",
    "review status": "status", "action": "status", "result": "status",
    "ball in court": "ball_in_court", "ball-in-court": "ball_in_court", "bic": "ball_in_court",
    "assigned to": "ball_in_court", "responsible": "ball_in_court",
    "held by": "ball_in_court", "reviewer": "ball_in_court",
    "submitted": "submitted_date", "submitted date": "submitted_date",
    "date submitted": "submitted_date", "received": "submitted_date", "received date": "submitted_date",
    "due": "due_date", "due date": "due_date", "required": "due_date",
    "required by": "due_date", "need by": "due_date",
    "returned": "returned_date", "returned date": "returned_date",
    "date returned": "returned_date", "reviewed date": "returned_date", "response date": "returned_date",
    "revision": "revision", "rev": "revision", "submission": "revision",
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


def read_submittals(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return [normalize_row(r) for r in csv.DictReader(fh)]


def enrich(rows: list[dict], as_of: date) -> list[dict]:
    for r in rows:
        s = r["status"].strip().lower()
        r["_complete"] = s in COMPLETE
        r["_resubmit"] = s in RESUBMIT
        due = parse_date(r["due_date"])
        r["overdue"] = "yes" if (due and due < as_of and not r["_complete"]) else "no"
        sub = parse_date(r["submitted_date"])
        ret = parse_date(r["returned_date"])
        r["cycle_days"] = (ret - sub).days if (sub and ret) else None
    return rows


def summarize(rows: list[dict], as_of: date) -> str:
    open_rows = [r for r in rows if not r["_complete"]]
    L = [f"Submittal log — mốc so hạn / as of: {as_of.isoformat()}",
         f"Tổng / Total: {len(rows)}  |  đang mở / open: {len(open_rows)}  "
         f"|  hoàn tất / complete: {len(rows) - len(open_rows)}", ""]

    L.append("Theo trạng thái / By status:")
    for val, n in Counter(r["status"] or "(blank)" for r in rows).most_common():
        L.append(f"  {n:4}  {val}")
    L.append("")

    L.append("Ball-in-court (đang mở / open only):")
    for val, n in Counter(r["ball_in_court"] or "(blank)" for r in open_rows).most_common():
        L.append(f"  {n:4}  {val}")
    L.append("")

    if any(r["spec_section"] for r in rows):
        L.append("Theo spec section:")
        for val, n in Counter(r["spec_section"] or "(blank)" for r in rows).most_common(10):
            L.append(f"  {n:4}  {val}")
        L.append("")

    resubmit = [r for r in rows if r["_resubmit"]]
    L.append(f"Cần nộp lại / Revise & resubmit: {len(resubmit)}")

    overdue = [r for r in open_rows if r["overdue"] == "yes"]
    L.append(f"Quá hạn / Overdue: {len(overdue)}")
    for r in overdue:
        L.append(f"  - {r['id']} {r['title']}  (due {r['due_date']}, "
                 f"BIC {r['ball_in_court'] or '?'})")
    L.append("")

    cycles = [r["cycle_days"] for r in rows if r["cycle_days"] is not None]
    if cycles:
        L.append(f"Chu kỳ review (ngày nhận→trả) / Review cycle: "
                 f"tb/avg {statistics.mean(cycles):.1f}d, "
                 f"trung vị/median {statistics.median(cycles):.0f}d, max {max(cycles)}d")
    return "\n".join(L)


def write_csv(rows: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = CANON + ["overdue", "cycle_days"]
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Normalize & track a submittal register.")
    ap.add_argument("csv", help="File CSV submittal register")
    ap.add_argument("--as-of", help="Mốc so hạn YYYY-MM-DD (mặc định hôm nay)")
    ap.add_argument("--csv", dest="out_csv", help="Xuất log CSV có cột tính toán")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2
    as_of = parse_date(args.as_of) or date.today()

    rows = enrich(read_submittals(path), as_of)
    print(summarize(rows, as_of))
    if args.out_csv:
        write_csv(rows, Path(args.out_csv))
        print(f"\nĐã ghi log / wrote log: {args.out_csv} ({len(rows)} dòng)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
