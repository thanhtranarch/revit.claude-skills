#!/usr/bin/env python3
"""
check_cobie.py — Kiểm tính đầy đủ của một sheet COBie (CSV export).
                 Validate completeness of a COBie sheet (CSV export).

Kiểm: đủ cột bắt buộc, ô bắt buộc không rỗng, Name không trùng, CreatedBy là
email, CreatedOn đúng ISO 8601. Chỉ dùng thư viện chuẩn.
Checks required columns, non-empty required cells, unique Name, email CreatedBy
and ISO 8601 CreatedOn. Stdlib only.

Usage:
    python check_cobie.py component.csv --sheet Component
    python check_cobie.py space.csv            # tự dò loại sheet / auto-detect
Exit: 0 = đạt, 1 = có lỗi, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# Cột bắt buộc theo từng sheet COBie / required columns per COBie sheet.
COBIE_SHEETS = {
    "facility": ["Name", "CreatedBy", "CreatedOn", "Category", "ProjectName",
                 "SiteName", "LinearUnits", "AreaUnits", "VolumeUnits"],
    "floor": ["Name", "CreatedBy", "CreatedOn", "Category"],
    "space": ["Name", "CreatedBy", "CreatedOn", "Category", "FloorName"],
    "zone": ["Name", "CreatedBy", "CreatedOn", "Category", "SpaceNames"],
    "type": ["Name", "CreatedBy", "CreatedOn", "Category"],
    "component": ["Name", "CreatedBy", "CreatedOn", "TypeName", "Space"],
    "system": ["Name", "CreatedBy", "CreatedOn", "Category", "ComponentNames"],
}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ISO_FORMATS = ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ")


def is_iso(s: str) -> bool:
    for fmt in ISO_FORMATS:
        try:
            datetime.strptime(s, fmt)
            return True
        except ValueError:
            continue
    return False


def detect_sheet(headers: list[str]) -> str:
    low = {h.strip().lower() for h in headers}
    best, best_score = "component", -1
    for name, req in COBIE_SHEETS.items():
        score = sum(1 for c in req if c.lower() in low)
        if score > best_score:
            best, best_score = name, score
    return best


def col_lookup(headers: list[str], name: str):
    low = {h.strip().lower(): h for h in headers}
    return low.get(name.lower())


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate a COBie sheet for completeness.")
    ap.add_argument("csv", help="CSV export của một sheet COBie")
    ap.add_argument("--sheet", choices=sorted(COBIE_SHEETS), help="Loại sheet (mặc định tự dò)")
    ap.add_argument("--limit", type=int, default=20, help="Số ví dụ lỗi tối đa mỗi loại")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        rows = list(reader)

    sheet = args.sheet or detect_sheet(headers)
    required = COBIE_SHEETS[sheet]
    print(f"COBie validation — sheet: {sheet.capitalize()}  ({len(rows)} dòng / rows)")
    print(f"Cột bắt buộc / required: {', '.join(required)}")
    print("-" * 68)

    errors = 0

    # 1. cột bắt buộc / required columns present
    missing_cols = [c for c in required if not col_lookup(headers, c)]
    present = [c for c in required if col_lookup(headers, c)]
    if missing_cols:
        errors += len(missing_cols)
        print(f"🔴 Thiếu cột bắt buộc / missing columns: {missing_cols}")

    # 2. ô rỗng ở cột bắt buộc / empty required cells
    for c in present:
        col = col_lookup(headers, c)
        empties = [i for i, r in enumerate(rows, 1) if not (r.get(col) or "").strip()]
        if empties:
            errors += len(empties)
            ex = ", ".join(f"dòng/row {i}" for i in empties[:args.limit])
            more = f" (+{len(empties) - args.limit})" if len(empties) > args.limit else ""
            print(f"🔴 Cột '{c}' rỗng {len(empties)} ô / empty: {ex}{more}")

    # 3. Name không trùng / unique Name
    name_col = col_lookup(headers, "Name")
    if name_col:
        counts = Counter((r.get(name_col) or "").strip() for r in rows if (r.get(name_col) or "").strip())
        dupes = {n: c for n, c in counts.items() if c > 1}
        if dupes:
            errors += len(dupes)
            print(f"🔴 Name trùng / duplicate Name: "
                  + ", ".join(f"{n}×{c}" for n, c in list(dupes.items())[:args.limit]))

    # 4. CreatedBy email + CreatedOn ISO (cảnh báo định dạng / format warnings)
    warnings = 0
    cb_col = col_lookup(headers, "CreatedBy")
    if cb_col:
        bad = [(r.get(name_col) or f"#{i}") for i, r in enumerate(rows, 1)
               if (r.get(cb_col) or "").strip() and not EMAIL_RE.match((r.get(cb_col) or "").strip())]
        if bad:
            warnings += len(bad)
            print(f"🟡 CreatedBy không phải email / not an email: {bad[:args.limit]}")
    co_col = col_lookup(headers, "CreatedOn")
    if co_col:
        bad = [(r.get(name_col) or f"#{i}") for i, r in enumerate(rows, 1)
               if (r.get(co_col) or "").strip() and not is_iso((r.get(co_col) or "").strip())]
        if bad:
            warnings += len(bad)
            print(f"🟡 CreatedOn không đúng ISO 8601 / bad date: {bad[:args.limit]}")

    print("-" * 68)
    print(f"{'⛔' if errors else '✅'} lỗi / errors: {errors}   🟡 cảnh báo / warnings: {warnings}")
    if errors:
        print("→ COBie yêu cầu mọi ô bắt buộc có giá trị (dùng 'n/a' nếu không áp dụng), "
              "Name duy nhất, CreatedBy/CreatedOn hợp lệ.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
