#!/usr/bin/env python3
"""
weekly_report.py — Tổng hợp báo cáo trạng thái tuần từ nhiều register CSV.
                   Assemble a weekly status report from multiple register CSVs.

Nhận nhiều nguồn (issue log, RFI, clash, change order...), tự dò cột
status/due, đếm open/closed/overdue, và xuất Markdown. Có thể lưu snapshot
JSON và so sánh tuần trước (week-over-week). Chỉ dùng thư viện chuẩn.
Reads several sources, auto-detects status/due columns, counts
open/closed/overdue, and emits Markdown. Optional JSON snapshot + prior-week
delta. Stdlib only.

Usage:
    python weekly_report.py --source Issues=issues.csv --source RFIs=rfis.csv
    python weekly_report.py --source Issues=issues.csv --as-of 2026-07-24 \
           --prev last_week.json --snapshot this_week.json --out report.md
Exit: 0 = ok, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path

CLOSED_STATES = {
    "closed", "resolved", "answered", "approved", "approved as noted",
    "done", "complete", "completed", "void", "not an issue", "rejected",
    "cancelled", "canceled",
}
STATUS_ALIASES = ["status", "state", "disposition"]
DUE_ALIASES = ["due", "due date", "response due", "target", "target date",
               "deadline", "date required", "required by", "answer due"]
ID_ALIASES = ["id", "no", "number", "ref", "rfi", "rfi number", "co", "co number",
              "item", "issue id", "clash id", "clash name"]
TITLE_ALIASES = ["title", "subject", "name", "description", "action", "question"]
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


def find_col(headers: list[str], aliases: list[str]):
    low = {h.strip().lower(): h for h in headers}
    for a in aliases:
        if a in low:
            return low[a]
    return None


def analyze_source(path: Path, as_of: date) -> dict:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        rows = list(reader)
    status_col = find_col(headers, STATUS_ALIASES)
    due_col = find_col(headers, DUE_ALIASES)
    id_col = find_col(headers, ID_ALIASES)
    title_col = find_col(headers, TITLE_ALIASES)

    total = open_ = closed = 0
    overdue_items: list[tuple[str, str, str]] = []
    for r in rows:
        total += 1
        status = (r.get(status_col) or "").strip() if status_col else ""
        is_closed = status.lower() in CLOSED_STATES
        if is_closed:
            closed += 1
            continue
        open_ += 1
        due = parse_date(r.get(due_col) or "") if due_col else None
        if due and due < as_of:
            ident = (r.get(id_col) or "").strip() if id_col else ""
            title = (r.get(title_col) or "").strip() if title_col else ""
            overdue_items.append((ident, title, due.isoformat()))
    return {
        "total": total, "open": open_, "closed": closed,
        "overdue": len(overdue_items), "overdue_items": overdue_items,
    }


def fmt_delta(cur: int, prev) -> str:
    if prev is None:
        return "—"
    d = cur - prev
    return "0" if d == 0 else f"+{d}" if d > 0 else str(d)


def build_markdown(results: dict, as_of: date, prev: dict, title: str) -> str:
    L = [f"# {title} — {as_of.isoformat()}", ""]
    L.append("| Nguồn / Source | Total | Open | Closed | Overdue | Δ Open |")
    L.append("|----------------|------:|-----:|-------:|--------:|-------:|")
    tot = {"total": 0, "open": 0, "closed": 0, "overdue": 0}
    for label, s in results.items():
        prev_open = (prev.get(label) or {}).get("open") if prev else None
        L.append(f"| {label} | {s['total']} | {s['open']} | {s['closed']} "
                 f"| {s['overdue']} | {fmt_delta(s['open'], prev_open)} |")
        for k in tot:
            tot[k] += s[k]
    L.append(f"| **Tổng / Total** | {tot['total']} | {tot['open']} | "
             f"{tot['closed']} | {tot['overdue']} | |")
    L.append("")

    for label, s in results.items():
        if not s["overdue_items"]:
            continue
        L.append(f"## Quá hạn / Overdue — {label} ({s['overdue']})")
        for ident, title_i, due in s["overdue_items"]:
            tag = " ".join(x for x in (ident, title_i) if x) or "(item)"
            L.append(f"- {tag} — due {due}")
        L.append("")
    return "\n".join(L).rstrip() + "\n"


def parse_source(spec: str) -> tuple[str, Path]:
    if "=" not in spec:
        raise argparse.ArgumentTypeError(f"--source phải là LABEL=path.csv (nhận '{spec}')")
    label, path = spec.split("=", 1)
    return label.strip(), Path(path.strip())


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Assemble a weekly status report from registers.")
    ap.add_argument("--source", action="append", type=parse_source, metavar="LABEL=path.csv",
                    help="Nguồn CSV (lặp lại nhiều lần)")
    ap.add_argument("--as-of", help="Mốc so hạn YYYY-MM-DD (mặc định hôm nay)")
    ap.add_argument("--title", default="Weekly Status Report", help="Tiêu đề báo cáo")
    ap.add_argument("--prev", help="Snapshot JSON tuần trước (để tính Δ)")
    ap.add_argument("--snapshot", help="Ghi snapshot JSON tuần này")
    ap.add_argument("--out", help="Ghi báo cáo Markdown ra file")
    args = ap.parse_args(argv)

    if not args.source:
        print("ERROR: cần ít nhất một --source LABEL=path.csv", file=sys.stderr)
        return 2
    as_of = parse_date(args.as_of) or date.today()

    prev = {}
    if args.prev:
        p = Path(args.prev)
        if not p.is_file():
            print(f"ERROR: không tìm thấy --prev: {args.prev}", file=sys.stderr)
            return 2
        prev = json.loads(p.read_text(encoding="utf-8"))

    results: dict[str, dict] = {}
    for label, path in args.source:
        if not path.is_file():
            print(f"ERROR: không tìm thấy nguồn: {path}", file=sys.stderr)
            return 2
        results[label] = analyze_source(path, as_of)

    md = build_markdown(results, as_of, prev, args.title)
    print(md)

    if args.snapshot:
        snap = {label: {k: s[k] for k in ("total", "open", "closed", "overdue")}
                for label, s in results.items()}
        Path(args.snapshot).parent.mkdir(parents=True, exist_ok=True)
        Path(args.snapshot).write_text(json.dumps(snap, ensure_ascii=False, indent=2),
                                       encoding="utf-8")
        print(f"[snapshot ghi / wrote] {args.snapshot}", file=sys.stderr)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(md, encoding="utf-8")
        print(f"[report ghi / wrote] {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
