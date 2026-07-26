#!/usr/bin/env python3
"""
plan_sheets.py — Kiểm & lập kế hoạch tạo sheet hàng loạt từ danh sách (CSV).
                 Validate & plan batch sheet creation from a sheet list (CSV).

Kiểm số sheet (pattern + trùng), tên rỗng; gom theo bộ môn; xuất plan JSON để
template pyRevit tạo sheet. Chỉ dùng thư viện chuẩn.

Usage:
    python plan_sheets.py sheets.csv
    python plan_sheets.py sheets.csv --json > sheets.json
Exit: 0 = sẵn sàng (không lỗi), 1 = có lỗi cần sửa, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

NUMBER_COLS = ["sheet number", "sheet no", "number", "no", "drawing number", "dwg no"]
NAME_COLS = ["sheet name", "name", "title", "sheet title", "drawing title"]
TB_COLS = ["titleblock", "title block", "tb", "title block type"]
DISC_COLS = ["discipline", "disc"]
NUMBER_RE = re.compile(r"^[A-Z]{1,2}[-.]?\d{2,4}[A-Z]?$")


def find_col(headers, aliases):
    low = {h.strip().lower(): h for h in headers}
    for a in aliases:
        if a in low:
            return low[a]
    return None


def read_rows(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        cols = {
            "number": find_col(headers, NUMBER_COLS), "name": find_col(headers, NAME_COLS),
            "tb": find_col(headers, TB_COLS), "disc": find_col(headers, DISC_COLS),
        }
        if not cols["number"]:
            print(f"ERROR: không dò được cột số sheet trong {headers}", file=sys.stderr)
            sys.exit(2)
        rows = [{k: (r.get(c) or "").strip() if c else "" for k, c in cols.items()} for r in reader]
    return rows


def discipline_of(row: dict) -> str:
    if row["disc"]:
        return row["disc"]
    m = re.match(r"^[A-Za-z]+", row["number"])
    return m.group().upper() if m else "(?)"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate & plan batch sheet creation.")
    ap.add_argument("csv", help="CSV danh sách sheet")
    ap.add_argument("--json", action="store_true", help="Xuất plan JSON cho template pyRevit")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2
    rows = read_rows(path)
    if not rows:
        print("Không có sheet nào trong danh sách.", file=sys.stderr)
        return 2

    counts = Counter(r["number"].upper() for r in rows if r["number"])
    dupes = {n for n, c in counts.items() if c > 1}

    issues: list[str] = []
    ready: list[dict] = []
    for r in rows:
        num = r["number"]
        row_issues = []
        if not num:
            row_issues.append("thiếu số / missing number")
        else:
            if num.upper() in dupes:
                row_issues.append("số trùng / duplicate number")
            if not NUMBER_RE.match(num.upper()):
                row_issues.append("số sai pattern / bad number pattern")
        if not r["name"]:
            row_issues.append("thiếu tên / missing name")
        if row_issues:
            issues.append(f"{num or '(blank)'} {r['name']}: " + "; ".join(row_issues))
        else:
            ready.append({"number": num, "name": r["name"], "titleblock": r["tb"]})

    if args.json:
        print(json.dumps({"count": len(ready), "sheets": ready}, ensure_ascii=False, indent=2))
        return 1 if issues else 0

    print(f"Sheet creation plan — {len(rows)} dòng / rows")
    by_disc = Counter(discipline_of(r) for r in rows if r["number"])
    print("Theo bộ môn / by discipline:")
    for disc, n in sorted(by_disc.items()):
        print(f"  {disc:4} {n}")
    print()
    if issues:
        print(f"🔴 Lỗi cần sửa / issues ({len(issues)}):")
        for i in issues:
            print(f"  - {i}")
        print()
    print(f"{'✅' if not issues else '⚠'} Sẵn sàng tạo / ready to create: {len(ready)}"
          f"{'  (xuất --json cho template pyRevit)' if ready else ''}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
