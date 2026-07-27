#!/usr/bin/env python3
"""
check_sheet_naming.py — Kiểm tra số & tên sheet theo chuẩn công ty.
                        Validate sheet numbers & names against a company standard.

Đầu vào: CSV export sheet list (Sheet Number, Sheet Name). Kiểm số sheet theo
regex + prefix bộ môn cho phép, bắt **số trùng**, tên rỗng và **từ cấm** trong
tên (Copy/Draft/DO NOT USE...). Chỉ dùng thư viện chuẩn; --rules cần pyyaml.

Usage:
    python check_sheet_naming.py sheets.csv
    python check_sheet_naming.py sheets.csv --rules my_rules.yaml
Exit: 0 = tất cả đạt, 1 = có lỗi/trùng, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

DEFAULT_RULES = {
    # prefix bộ môn (1–2 chữ) + dấu tuỳ chọn + 2–4 số + hậu tố chữ tuỳ chọn.
    "number_pattern": r"^[A-Z]{1,2}[-.]?\d{2,4}[A-Z]?$",
    "allowed_disciplines": ["A", "S", "M", "E", "P", "C", "L", "FP", "T", "G", "ID"],
    "forbidden_name_terms": ["copy", "draft", "do not use", "test", "temp", "xxx", "tbc"],
    "require_name": True,
}
NUMBER_COLS = ["sheet number", "sheet no", "number", "no", "sheet", "drawing number", "dwg no"]
NAME_COLS = ["sheet name", "name", "title", "sheet title", "drawing title", "description"]


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


def find_col(headers: list[str], candidates: list[str]):
    low = {h.strip().lower(): h for h in headers}
    for c in candidates:
        if c in low:
            return low[c]
    return None


def read_sheets(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        num_col = find_col(headers, NUMBER_COLS)
        name_col = find_col(headers, NAME_COLS)
        if not num_col:
            print(f"ERROR: không dò được cột Sheet Number trong {headers}", file=sys.stderr)
            sys.exit(2)
        return [{"number": (r.get(num_col) or "").strip(),
                 "name": (r.get(name_col) or "").strip() if name_col else ""}
                for r in reader]


def check_sheet(number: str, name: str, rules: dict) -> list[str]:
    errs: list[str] = []
    num = number.upper()
    pattern = rules.get("number_pattern")
    if pattern and not re.match(pattern, num):
        errs.append(f"số sai pattern / bad number pattern ({pattern})")
    allowed = rules.get("allowed_disciplines")
    if allowed:
        m = re.match(r"^[A-Z]+", num)
        prefix = m.group() if m else ""
        if prefix not in allowed:
            errs.append(f"prefix bộ môn '{prefix or '?'}' không thuộc {allowed}")
    if rules.get("require_name") and not name:
        errs.append("thiếu tên sheet / missing sheet name")
    low_name = name.lower()
    for term in rules.get("forbidden_name_terms", []):
        if term in low_name:
            errs.append(f"tên chứa từ cấm / forbidden term: '{term}'")
    return errs


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate Revit/CAD sheet numbers & names.")
    ap.add_argument("csv", help="CSV export sheet list")
    ap.add_argument("--rules", help="YAML ghi đè rule")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2
    rules = load_rules(args.rules)
    sheets = read_sheets(path)
    if not sheets:
        print("Không có sheet nào để kiểm.", file=sys.stderr)
        return 2

    # số trùng / duplicate numbers (chuẩn hoá hoa + bỏ khoảng trắng)
    counts = Counter(s["number"].upper() for s in sheets if s["number"])
    dupes = {num for num, n in counts.items() if n > 1}

    n_pass = n_fail = 0
    for s in sheets:
        errs = check_sheet(s["number"], s["name"], rules)
        if s["number"].upper() in dupes:
            errs.append(f"số trùng / duplicate number (×{counts[s['number'].upper()]})")
        label = f"{s['number'] or '(blank)'}  {s['name']}".rstrip()
        if errs:
            n_fail += 1
            print(f"FAIL  {label}")
            for e in errs:
                print(f"        - {e}")
        else:
            n_pass += 1
            print(f"PASS  {label}")

    print(f"\nTổng: {len(sheets)}  |  đạt/pass: {n_pass}  |  lỗi/fail: {n_fail}  "
          f"|  số trùng/duplicate numbers: {len(dupes)}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
