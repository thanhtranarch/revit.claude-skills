#!/usr/bin/env python3
"""
audit_family_names.py — Kiểm tra tên family/type Revit theo chuẩn công ty.
                        Audit Revit family/type names against a naming standard.

Đầu vào: CSV export danh sách family (cột Family, Type, Category). Kiểm pattern
tên family, prefix bộ môn cho phép, khoảng trắng / gạch dưới lỗi; bắt family
dùng lại tên qua nhiều category và (Family,Type) trùng lặp.
Chỉ dùng thư viện chuẩn; --rules cần pyyaml.

Usage:
    python audit_family_names.py families.csv
    python audit_family_names.py families.csv --rules my_rules.yaml --check-types
Exit: 0 = tất cả đạt, 1 = có lỗi, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

DEFAULT_RULES = {
    # prefix bộ môn + các đoạn phân tách bằng "_" hoặc "-", không khoảng trắng.
    "name_pattern": r"^[A-Z]{2,3}_[A-Za-z0-9]+(?:[_-][A-Za-z0-9]+)*$",
    "allowed_prefixes": ["AR", "ST", "ME", "EL", "PL", "FP", "CI",
                         "LS", "GN", "FF", "SP", "SE"],
    "prefix_delim": "_",
    "forbid_spaces": True,
    "type_pattern": r"^[A-Za-z0-9]+(?:[ _\-x×]+[A-Za-z0-9]+)*$",
}
FAMILY_COLS = ["family", "family name", "family_name", "familyname"]
TYPE_COLS = ["type", "type name", "type_name", "family type", "symbol"]
CATEGORY_COLS = ["category", "cat", "revit category"]


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


def read_rows(path: Path) -> tuple[list[dict], str, str, str]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        fam = find_col(headers, FAMILY_COLS)
        typ = find_col(headers, TYPE_COLS)
        cat = find_col(headers, CATEGORY_COLS)
        if not fam:
            print(f"ERROR: không dò được cột Family trong {headers}", file=sys.stderr)
            sys.exit(2)
        rows = [{"family": (r.get(fam) or "").strip(),
                 "type": (r.get(typ) or "").strip() if typ else "",
                 "category": (r.get(cat) or "").strip() if cat else ""}
                for r in reader]
    return rows, fam, typ or "", cat or ""


def check_family_name(name: str, rules: dict) -> list[str]:
    errs: list[str] = []
    if rules.get("forbid_spaces") and " " in name:
        errs.append("có khoảng trắng / contains space")
    if "__" in name:
        errs.append("gạch dưới đôi '__' / double underscore")
    if name.startswith(("_", "-")) or name.endswith(("_", "-")):
        errs.append("gạch dưới/gạch nối ở đầu hoặc cuối")
    pattern = rules.get("name_pattern")
    if pattern and not re.match(pattern, name):
        errs.append(f"sai pattern / bad pattern ({pattern})")
    delim = rules.get("prefix_delim", "_")
    allowed = rules.get("allowed_prefixes")
    if allowed:
        prefix = name.split(delim)[0]
        if prefix not in allowed:
            errs.append(f"prefix '{prefix}' không thuộc danh mục {allowed}")
    return errs


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Audit Revit family/type names.")
    ap.add_argument("csv", help="CSV export family (Family, Type, Category)")
    ap.add_argument("--rules", help="YAML ghi đè rule (pattern, allowed_prefixes...)")
    ap.add_argument("--check-types", action="store_true", help="Kiểm cả tên type")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2
    rules = load_rules(args.rules)
    rows, _, _, _ = read_rows(path)
    if not rows:
        print("Không có family nào để kiểm.", file=sys.stderr)
        return 2

    # gom theo family: các category dùng chung tên, và đếm (family,type)
    fam_categories: dict[str, set] = defaultdict(set)
    pair_counter: Counter = Counter()
    for r in rows:
        if r["family"]:
            fam_categories[r["family"]].add(r["category"] or "(no category)")
            pair_counter[(r["family"], r["type"])] += 1

    n_pass = n_fail = 0
    for fam in sorted(fam_categories):
        errs = check_family_name(fam, rules)
        cats = fam_categories[fam]
        if len(cats) > 1:
            errs.append(f"tên dùng lại qua nhiều category / reused across categories: {sorted(cats)}")
        if errs:
            n_fail += 1
            print(f"FAIL  {fam}")
            for e in errs:
                print(f"        - {e}")
        else:
            n_pass += 1
            print(f"PASS  {fam}")

    if args.check_types:
        tpat = rules.get("type_pattern")
        bad_types = sorted({(f, t) for (f, t) in pair_counter
                            if t and tpat and not re.match(tpat, t)})
        if bad_types:
            print("\nType sai pattern / non-conforming types:")
            for f, t in bad_types:
                print(f"  - {f}  ::  {t}")

    dupes = [(pair, n) for pair, n in pair_counter.items() if n > 1]
    if dupes:
        print("\n(Family, Type) trùng lặp / duplicate pairs:")
        for (f, t), n in sorted(dupes):
            print(f"  - {f}  ::  {t}  ×{n}")

    print(f"\nFamily riêng biệt / distinct: {len(fam_categories)}  |  "
          f"đạt/pass: {n_pass}  |  lỗi/fail: {n_fail}  |  "
          f"cặp trùng/dup pairs: {len(dupes)}")
    return 1 if (n_fail or dupes) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
