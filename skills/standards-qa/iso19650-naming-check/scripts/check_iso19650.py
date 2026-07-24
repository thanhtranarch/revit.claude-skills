#!/usr/bin/env python3
"""
check_iso19650.py — Kiểm tra tên file theo quy ước ISO 19650 / UK BIM Framework.
                    Validate file names against the ISO 19650 naming convention.

Đầu vào: CSV (có cột tên file) hoặc .txt (mỗi dòng 1 tên).
Chỉ dùng thư viện chuẩn; --rules cần pyyaml.

Usage:
    python check_iso19650.py register.csv
    python check_iso19650.py filenames.txt
    python check_iso19650.py register.csv --name-col "File Name" \
           --status-col Suitability --rev-col Revision --rules my_rules.yaml
Exit: 0 = tất cả đạt, 1 = có lỗi, 2 = usage.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

# --- Quy tắc mặc định (UK BIM Framework) — tuỳ biến qua --rules ------------
DEFAULT_RULES = {
    "field_delimiter": "-",
    "fields": [
        {"name": "Project", "pattern": r"^[A-Z0-9]{2,6}$"},
        {"name": "Originator", "pattern": r"^[A-Z0-9]{3,6}$"},
        {"name": "Volume", "pattern": r"^[A-Z0-9]{1,2}$"},
        {"name": "Location", "pattern": r"^[A-Z0-9]{2}$"},
        {"name": "Type", "allowed": [
            "AF", "BQ", "CA", "CM", "CO", "CP", "CR", "DB", "DR", "FN", "HS",
            "IE", "M2", "M3", "MI", "MR", "MS", "PP", "PR", "RD", "RI", "RP",
            "RT", "SA", "SH", "SN", "SP", "SU", "VS", "ZZ",
        ]},
        {"name": "Role", "allowed": list("ABCDEFGHIKLMPQSTWXYZ")},
        {"name": "Number", "pattern": r"^[0-9]{4,}$"},
    ],
    # tuỳ chọn: nếu tên file có thêm trường status/revision ở cuối, hoặc lấy từ cột CSV
    "status_allowed": [
        "S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7",
        "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9",
        "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9",
        "CR", "D1", "D2", "D3", "D4",
    ],
    "revision_pattern": r"^[PC][0-9]{2}(\.[0-9]{1,2})?$",
}

NAME_COL_CANDIDATES = ["file name", "filename", "file", "name", "document name",
                       "container", "container name"]


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


def validate_field(value: str, spec: dict) -> str | None:
    """Trả về thông báo lỗi hoặc None nếu đạt."""
    if "allowed" in spec:
        if value not in spec["allowed"]:
            return f"{spec['name']}='{value}' không thuộc danh mục cho phép"
    if "pattern" in spec:
        if not re.match(spec["pattern"], value):
            return f"{spec['name']}='{value}' sai định dạng ({spec['pattern']})"
    return None


def check_name(name: str, rules: dict, status: str = "", revision: str = "") -> list[str]:
    errors: list[str] = []
    delim = rules["field_delimiter"]
    fields = rules["fields"]
    n_core = len(fields)

    parts = name.split(delim)
    if len(parts) < n_core:
        return [f"Thiếu trường: có {len(parts)}, cần ≥{n_core} "
                f"({'-'.join(f['name'] for f in fields)})"]

    for spec, value in zip(fields, parts):
        err = validate_field(value, spec)
        if err:
            errors.append(err)

    # trường status/revision: ưu tiên cột CSV, nếu không có thì lấy field dư trong tên
    extra = parts[n_core:]
    status = status or (extra[0] if len(extra) >= 1 else "")
    revision = revision or (extra[1] if len(extra) >= 2 else "")

    if status:
        if status not in rules.get("status_allowed", []):
            errors.append(f"Status='{status}' không thuộc danh mục suitability")
    if revision:
        if not re.match(rules.get("revision_pattern", r".*"), revision):
            errors.append(f"Revision='{revision}' sai định dạng")
    return errors


def read_inputs(path: Path, name_col: str | None, status_col: str | None,
                rev_col: str | None) -> list[dict]:
    items: list[dict] = []
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            headers = reader.fieldnames or []
            col = name_col or _autodetect(headers)
            if not col:
                print(f"ERROR: không dò được cột tên file trong {headers}. "
                      f"Dùng --name-col.", file=sys.stderr)
                sys.exit(2)
            for row in reader:
                items.append({
                    "name": (row.get(col) or "").strip(),
                    "status": (row.get(status_col) or "").strip() if status_col else "",
                    "revision": (row.get(rev_col) or "").strip() if rev_col else "",
                })
    else:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip():
                items.append({"name": line.strip(), "status": "", "revision": ""})
    return items


def _autodetect(headers: list[str]) -> str | None:
    lower = {h.lower(): h for h in headers}
    for cand in NAME_COL_CANDIDATES:
        if cand in lower:
            return lower[cand]
    return None


def strip_ext(name: str) -> str:
    # bỏ đuôi mở rộng phổ biến để lấy phần mã
    return re.sub(r"\.(pdf|dwg|rvt|nwc|nwd|ifc|docx?|xlsx?|txt)$", "", name, flags=re.I)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="ISO 19650 file naming checker.")
    ap.add_argument("input", help="CSV register hoặc .txt danh sách tên")
    ap.add_argument("--name-col")
    ap.add_argument("--status-col")
    ap.add_argument("--rev-col")
    ap.add_argument("--rules")
    args = ap.parse_args(argv)

    path = Path(args.input)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.input}", file=sys.stderr)
        return 2

    rules = load_rules(args.rules)
    items = read_inputs(path, args.name_col, args.status_col, args.rev_col)
    if not items:
        print("Không có tên file nào để kiểm.", file=sys.stderr)
        return 2

    n_pass, n_fail = 0, 0
    for it in items:
        name = strip_ext(it["name"])
        if not name:
            continue
        errs = check_name(name, rules, it["status"], it["revision"])
        if errs:
            n_fail += 1
            print(f"FAIL  {it['name']}")
            for e in errs:
                print(f"        - {e}")
        else:
            n_pass += 1
            print(f"PASS  {it['name']}")

    print(f"\nTổng: {n_pass + n_fail}  |  đạt: {n_pass}  |  lỗi: {n_fail}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
