#!/usr/bin/env python3
"""
check_schedule.py — Validate 1 schedule Revit (CSV/TSV) theo rules YAML.
                    Validate a Revit schedule export against a YAML rules file.

Kiểm: required (không trống), unique (duy nhất), allowed (giá trị hợp lệ).
Cần pyyaml + csv (stdlib).

Usage:
    python check_schedule.py schedule.csv --rules rules.yaml
Exit: 0 = không vi phạm, 1 = có vi phạm, 2 = lỗi sử dụng.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: cần pyyaml — chạy: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


def load_rules(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("rules file phải là mapping YAML")
    return data


def read_rows(path: Path, delimiter: str):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        return reader.fieldnames or [], list(reader)


def validate(rows, headers, rules) -> list[dict]:
    violations: list[dict] = []
    required = rules.get("required", []) or []
    unique = rules.get("unique", []) or []
    allowed = rules.get("allowed", {}) or {}

    # cột trong rules nhưng không có trong file
    for col in set(required) | set(unique) | set(allowed):
        if col not in headers:
            violations.append({"type": "MISSING COLUMN", "col": col, "row": "-",
                               "value": f"cột '{col}' không có trong schedule"})

    # data rows bắt đầu từ dòng 2 (dòng 1 = header)
    seen: dict[str, dict] = {c: {} for c in unique}
    for i, row in enumerate(rows, start=2):
        for col in required:
            if col in headers and not (row.get(col) or "").strip():
                violations.append({"type": "BLANK REQUIRED", "col": col, "row": i, "value": ""})
        for col, allow_list in allowed.items():
            if col in headers:
                val = (row.get(col) or "").strip()
                if val and val not in allow_list:
                    violations.append({"type": "NOT ALLOWED", "col": col, "row": i, "value": val})
        for col in unique:
            if col in headers:
                val = (row.get(col) or "").strip()
                if not val:
                    continue
                if val in seen[col]:
                    violations.append({"type": "DUPLICATE", "col": col, "row": i,
                                       "value": f"{val} (trùng dòng {seen[col][val]})"})
                else:
                    seen[col][val] = i
    return violations


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate a Revit schedule CSV against rules.")
    ap.add_argument("csv")
    ap.add_argument("--rules", required=True)
    args = ap.parse_args(argv)

    csv_path, rules_path = Path(args.csv), Path(args.rules)
    for p in (csv_path, rules_path):
        if not p.is_file():
            print(f"ERROR: không tìm thấy: {p}", file=sys.stderr)
            return 2

    rules = load_rules(rules_path)
    delimiter = rules.get("delimiter", ",")
    headers, rows = read_rows(csv_path, delimiter)
    violations = validate(rows, headers, rules)

    print(f"Schedule: {csv_path.name}  |  {len(rows)} dòng dữ liệu, {len(headers)} cột")
    if not violations:
        print("PASS: không có vi phạm.")
        return 0

    print(f"FAIL: {len(violations)} vi phạm:")
    for v in violations:
        print(f"  [{v['type']:14}] cột '{v['col']}' dòng {v['row']}: {v['value']}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
