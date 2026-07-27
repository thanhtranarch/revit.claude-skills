#!/usr/bin/env python3
"""
check_drawing_register.py — QA sổ phát hành bản vẽ (revision / suitability / ngày).
                            QA a drawing issue register (revision/status/dates).

Bắt: thiếu/sai định dạng revision, mã suitability không hợp lệ, thiếu ngày phát
hành, và số bản vẽ trùng. Bổ trợ `sheet-naming-check` (vốn kiểm pattern số/tên).
Chỉ dùng thư viện chuẩn; --rules cần pyyaml.

Usage:
    python check_drawing_register.py register.csv
    python check_drawing_register.py register.csv --rules my_rules.yaml
Exit: 0 = tất cả đạt, 1 = có lỗi, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

DEFAULT_RULES = {
    "revision_pattern": r"^(P\d{2}(\.\d{1,2})?|C\d{2}(\.\d{1,2})?|[A-Z]|\d{1,2})$",
    "status_allowed": [
        "S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7",
        "A1", "A2", "A3", "A4", "A5", "B1", "B2", "CR", "D1", "D2",
        "WIP", "Shared", "Published", "For Construction", "For Information",
    ],
    "require_revision": True,
    "require_issue_date": True,
    "require_status": False,
}
NUMBER_COLS = ["sheet number", "sheet no", "number", "drawing number", "dwg no", "no"]
TITLE_COLS = ["sheet name", "title", "drawing title", "name", "description"]
REV_COLS = ["revision", "rev", "current revision", "rev no", "revision no"]
STATUS_COLS = ["status", "suitability", "suitability code", "state", "purpose"]
DATE_COLS = ["issue date", "date", "issued", "date issued", "revision date"]


def load_rules(path: str | None) -> dict:
    rules = {**DEFAULT_RULES}
    if not path:
        return rules
    try:
        import yaml
    except ImportError:
        print("ERROR: --rules cần pyyaml (pip install pyyaml)", file=sys.stderr)
        sys.exit(2)
    user = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    rules.update(user)
    return rules


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
            "number": find_col(headers, NUMBER_COLS), "title": find_col(headers, TITLE_COLS),
            "rev": find_col(headers, REV_COLS), "status": find_col(headers, STATUS_COLS),
            "date": find_col(headers, DATE_COLS),
        }
        if not cols["number"]:
            print(f"ERROR: không dò được cột số bản vẽ trong {headers}", file=sys.stderr)
            sys.exit(2)
        rows = [{k: (r.get(c) or "").strip() if c else "" for k, c in cols.items()} for r in reader]
    return rows


def check_row(row: dict, rules: dict, dupes: set) -> list[str]:
    errs: list[str] = []
    num = row["number"]
    if not num:
        errs.append("thiếu số bản vẽ / missing sheet number")
    elif num.upper() in dupes:
        errs.append("số bản vẽ trùng / duplicate sheet number")

    rev = row["rev"]
    if not rev:
        if rules.get("require_revision"):
            errs.append("thiếu revision / missing revision")
    elif not re.match(rules["revision_pattern"], rev):
        errs.append(f"revision sai định dạng / bad revision format: '{rev}'")

    status = row["status"]
    allowed = {s.lower() for s in rules.get("status_allowed", [])}
    if not status:
        if rules.get("require_status"):
            errs.append("thiếu suitability / missing status")
    elif allowed and status.lower() not in allowed:
        errs.append(f"suitability không hợp lệ / invalid status: '{status}'")

    if rules.get("require_issue_date") and not row["date"]:
        errs.append("thiếu ngày phát hành / missing issue date")
    return errs


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="QA a drawing issue register.")
    ap.add_argument("csv", help="CSV drawing issue register")
    ap.add_argument("--rules", help="YAML ghi đè rule")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2
    rules = load_rules(args.rules)
    rows = read_rows(path)
    if not rows:
        print("Không có bản vẽ nào để kiểm.", file=sys.stderr)
        return 2

    counts = Counter(r["number"].upper() for r in rows if r["number"])
    dupes = {n for n, c in counts.items() if c > 1}

    n_pass = n_fail = 0
    for r in rows:
        errs = check_row(r, rules, dupes)
        label = f"{r['number'] or '(blank)'}  {r['title']}".rstrip()
        if errs:
            n_fail += 1
            print(f"FAIL  {label}")
            for e in errs:
                print(f"        - {e}")
        else:
            n_pass += 1
            print(f"PASS  {label}  (rev {r['rev']}, {r['status']}, {r['date']})")

    print(f"\nTổng: {len(rows)}  |  đạt/pass: {n_pass}  |  lỗi/fail: {n_fail}  "
          f"|  số trùng/duplicate numbers: {len(dupes)}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
