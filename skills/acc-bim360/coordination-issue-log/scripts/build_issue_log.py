#!/usr/bin/env python3
"""
build_issue_log.py — Gộp kết quả clash/coordination nhiều vòng thành issue log
                     có owner/discipline/status/target, sẵn sàng đẩy lên ACC.
                     Merge multi-round clash/coordination findings into a tracked
                     issue log, ready to push to ACC/BIM360 Issues.

Nhận nhiều CSV (mỗi vòng họp một file), gộp theo id (vòng sau đè vòng trước),
đánh dấu quá hạn theo target date, và (tuỳ chọn) xuất CSV khớp cột import Issues
của ACC. Chỉ dùng thư viện chuẩn.

Usage:
    python build_issue_log.py round1.csv round2.csv
    python build_issue_log.py *.csv --as-of 2026-07-24 --acc-csv out/acc_import.csv
Exit: 0 = ok, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

CANON = ["id", "title", "discipline", "owner", "status", "priority",
         "location", "raised_date", "target_date", "closed_date"]
CLOSED_STATES = {"closed", "resolved", "approved", "done", "verified", "complete", "completed"}

ALIASES = {
    "id": "id", "clash id": "id", "clash name": "id", "issue id": "id",
    "name": "id", "no": "id", "number": "id", "ref": "id",
    "title": "title", "description": "title", "subject": "title", "issue": "title", "clash": "title",
    "discipline": "discipline", "trade": "discipline", "disciplines": "discipline",
    "category": "discipline", "clash group": "discipline", "type": "discipline",
    "owner": "owner", "assignee": "owner", "assigned to": "owner", "responsible": "owner",
    "status": "status", "state": "status", "issue status": "status",
    "priority": "priority", "severity": "priority", "importance": "priority",
    "location": "location", "grid": "location", "level": "location",
    "zone": "location", "area": "location", "room": "location",
    "raised": "raised_date", "raised date": "raised_date", "date": "raised_date",
    "created": "raised_date", "found date": "raised_date", "identified": "raised_date",
    "target": "target_date", "target date": "target_date", "due": "target_date",
    "due date": "target_date", "deadline": "target_date",
    "closed": "closed_date", "closed date": "closed_date", "resolved date": "closed_date",
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


def merge(paths: list[Path]) -> tuple[dict, dict]:
    """Gộp nhiều file theo id (file sau đè file trước). Trả (log, source_of_id)."""
    log: dict[str, dict] = {}
    source: dict[str, str] = {}
    auto = 0
    for path in paths:
        with path.open(newline="", encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                row = normalize_row(r)
                key = row["id"]
                if not key:
                    auto += 1
                    key = f"{path.stem}#{auto}"
                    row["id"] = key
                if key in log:
                    # giữ raised_date sớm nhất; các trường khác lấy bản mới
                    prev_raised = log[key]["raised_date"]
                    if prev_raised and not row["raised_date"]:
                        row["raised_date"] = prev_raised
                log[key] = row
                source[key] = path.name
    return log, source


def enrich(rows: list[dict], as_of: date) -> list[dict]:
    for r in rows:
        closed = r["status"].strip().lower() in CLOSED_STATES or parse_date(r["closed_date"]) is not None
        target = parse_date(r["target_date"])
        r["_closed"] = closed
        r["overdue"] = "yes" if (target and target < as_of and not closed) else "no"
    return rows


def summarize(rows: list[dict], sources: dict, n_files: int, as_of: date) -> str:
    open_rows = [r for r in rows if not r["_closed"]]
    L = [f"Coordination issue log — mốc so hạn / as of: {as_of.isoformat()}",
         f"Gộp {n_files} file → {len(rows)} issue riêng biệt  |  đang mở / open: "
         f"{len(open_rows)}  |  đã đóng / closed: {len(rows) - len(open_rows)}", ""]

    for label, field in (("trạng thái / status", "status"),
                         ("bộ môn / discipline", "discipline"),
                         ("người phụ trách / owner", "owner")):
        L.append(f"Theo {label}:")
        for val, n in Counter(r[field] or "(blank)" for r in rows).most_common():
            L.append(f"  {n:4}  {val}")
        L.append("")

    overdue = [r for r in open_rows if r["overdue"] == "yes"]
    L.append(f"Quá hạn / Overdue: {len(overdue)}")
    for r in overdue:
        L.append(f"  - {r['id']} {r['title']}  (target {r['target_date']}, "
                 f"{r['owner'] or 'unassigned'})")
    return "\n".join(L)


def write_log_csv(rows: list[dict], sources: dict, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = CANON + ["source", "overdue"]
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            row = {k: r.get(k, "") for k in CANON}
            row["source"] = sources.get(r["id"], "")
            row["overdue"] = r["overdue"]
            w.writerow(row)


def write_acc_csv(rows: list[dict], out: Path) -> None:
    """Xuất khớp cột import Issues của ACC/BIM360 (điều chỉnh theo template dự án)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    header = ["Title", "Description", "Status", "Assignee", "Location", "Due Date"]
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for r in rows:
            desc = f"[{r['id']}] {r['discipline']}".strip()
            w.writerow([r["title"], desc, r["status"], r["owner"],
                        r["location"], r["target_date"]])


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Merge clash rounds into a coordination issue log.")
    ap.add_argument("csv", nargs="+", help="Một hoặc nhiều CSV clash/coordination")
    ap.add_argument("--as-of", help="Mốc so hạn YYYY-MM-DD (mặc định hôm nay)")
    ap.add_argument("--csv", dest="out_csv", help="Xuất log CSV đã gộp")
    ap.add_argument("--acc-csv", help="Xuất CSV khớp cột import Issues ACC/BIM360")
    args = ap.parse_args(argv)

    paths = [Path(p) for p in args.csv]
    for p in paths:
        if not p.is_file():
            print(f"ERROR: không tìm thấy: {p}", file=sys.stderr)
            return 2
    as_of = parse_date(args.as_of) or date.today()

    log, sources = merge(paths)
    rows = enrich(sorted(log.values(), key=lambda r: r["id"]), as_of)
    print(summarize(rows, sources, len(paths), as_of))
    if args.out_csv:
        write_log_csv(rows, sources, Path(args.out_csv))
        print(f"\nĐã ghi log / wrote log: {args.out_csv} ({len(rows)} dòng)")
    if args.acc_csv:
        write_acc_csv(rows, Path(args.acc_csv))
        print(f"Đã ghi ACC import / wrote ACC import: {args.acc_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
