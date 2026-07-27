#!/usr/bin/env python3
"""
build_type_catalog.py — Kiểm bảng type + sinh Revit type catalog (.txt) & plan JSON.
                        Validate a family-types table and emit a Revit type catalog
                        (.txt) plus a plan JSON for the pyRevit template.

Đọc CSV (mỗi dòng = một family type; các cột = tham số), kiểm hợp lệ, rồi xuất:
  • type catalog .txt đúng định dạng Revit (header ô đầu để trống,
    cột dạng `Name##TYPE##unit`), và
  • plan JSON để template pyRevit tạo type trong family đang mở.

Định dạng cột tham số trong CSV:
  - `Width##LENGTH##millimeters`  → dùng nguyên (name, kiểu, đơn vị).
  - `Fire Rating`                 → mặc định text (`Fire Rating##OTHER##`).
Cột đầu (hoặc cột tên `Type`/`Type Name`/`Name`) = tên type.

Chỉ dùng thư viện chuẩn. / Stdlib only.

Usage:
    python build_type_catalog.py types.csv                 # kiểm + xem tóm tắt
    python build_type_catalog.py types.csv --catalog Door.txt
    python build_type_catalog.py types.csv --json > plan.json
Exit: 0 = hợp lệ, 1 = có lỗi cần sửa, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

TYPE_NAME_COLS = {"type", "type name", "name", "type mark"}
# Kiểu tham số dimensional -> giá trị phải là số. / dimensional types require numbers.
NUMERIC_TYPES = {
    "LENGTH", "AREA", "VOLUME", "ANGLE", "NUMBER", "FORCE", "MASS",
    "CURRENCY", "SLOPE", "SPEED", "MASS_DENSITY",
}


def parse_param_header(header: str) -> dict:
    """`Name##TYPE##unit` -> {name, ptype, unit, raw}. Không có ## -> text (OTHER)."""
    parts = header.split("##")
    if len(parts) >= 3:
        name, ptype, unit = parts[0].strip(), parts[1].strip().upper(), parts[2].strip()
    else:
        name, ptype, unit = header.strip(), "OTHER", ""
    return {"name": name, "ptype": ptype or "OTHER", "unit": unit,
            "raw": f"{name}##{ptype or 'OTHER'}##{unit}"}


def read_table(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh)
        rows = [r for r in reader if any(c.strip() for c in r)]  # bỏ dòng rỗng
    if not rows:
        print("ERROR: file rỗng / empty file", file=sys.stderr)
        sys.exit(2)
    headers = [h.strip() for h in rows[0]]
    # xác định cột tên type
    name_idx = 0
    for i, h in enumerate(headers):
        if h.lower() in TYPE_NAME_COLS:
            name_idx = i
            break
    param_cols = [(i, parse_param_header(h)) for i, h in enumerate(headers) if i != name_idx]
    data = [dict(enumerate(r)) for r in rows[1:]]
    return headers, name_idx, param_cols, data


def validate(name_idx, param_cols, data) -> tuple[list[dict], list[str]]:
    issues: list[str] = []
    # trùng tên cột tham số
    pname_counts = Counter(p["name"].lower() for _, p in param_cols)
    for pname, c in pname_counts.items():
        if c > 1:
            issues.append(f"[DUPLICATE PARAM] cột tham số '{pname}' xuất hiện {c} lần")

    types: list[dict] = []
    seen: dict[str, int] = {}
    for rno, row in enumerate(data, start=2):
        tname = (row.get(name_idx) or "").strip()
        if not tname:
            issues.append(f"[BLANK TYPE] dòng {rno}: thiếu tên type")
            continue
        key = tname.lower()
        if key in seen:
            issues.append(f"[DUPLICATE TYPE] dòng {rno}: '{tname}' trùng dòng {seen[key]}")
            continue
        seen[key] = rno
        params: dict[str, str] = {}
        for idx, p in param_cols:
            val = (row.get(idx) or "").strip()
            if val and "," in val:
                issues.append(f"[COMMA IN VALUE] type '{tname}', cột '{p['name']}': "
                              f"giá trị chứa dấu phẩy sẽ phá vỡ type catalog: {val!r}")
            if val and p["ptype"] in NUMERIC_TYPES:
                try:
                    float(val)
                except ValueError:
                    issues.append(f"[NOT NUMBER] type '{tname}', cột '{p['name']}' "
                                  f"({p['ptype']}): '{val}' không phải số")
            params[p["name"]] = val
        types.append({"name": tname, "params": params})
    return types, issues


def render_catalog(param_cols, types) -> str:
    """Dòng đầu: ô rỗng + header cột; mỗi dòng sau: TypeName + giá trị. Phân tách bằng ','."""
    header = [""] + [p["raw"] for _, p in param_cols]
    lines = [",".join(header)]
    for t in types:
        lines.append(",".join([t["name"]] + [t["params"].get(p["name"], "") for _, p in param_cols]))
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate family types & build a Revit type catalog.")
    ap.add_argument("csv", help="CSV bảng type (dòng = type, cột = tham số)")
    ap.add_argument("--catalog", help="Ghi type catalog .txt ra file")
    ap.add_argument("--json", action="store_true", help="Xuất plan JSON cho template pyRevit")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2

    _, name_idx, param_cols, data = read_table(path)
    types, issues = validate(name_idx, param_cols, data)

    if args.json:
        plan = {"count": len(types),
                "parameters": [{"name": p["name"], "type": p["ptype"], "unit": p["unit"]}
                               for _, p in param_cols],
                "types": types}
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 1 if issues else 0

    catalog = render_catalog(param_cols, types)
    if args.catalog:
        out = Path(args.catalog)
        out.parent.mkdir(parents=True, exist_ok=True)
        # Revit type catalog: khuyến nghị lưu cùng tên .rfa, mã hoá UTF-8.
        out.write_text(catalog, encoding="utf-8")

    print(f"Family type catalog — {path.name}")
    print(f"  Type: {len(types)}  |  Tham số / params: {len(param_cols)}")
    if param_cols:
        print("  Cột / columns: " + ", ".join(f"{p['name']}[{p['ptype']}"
              + (f"|{p['unit']}]" if p['unit'] else "]") for _, p in param_cols))
    print()
    if issues:
        print(f"🔴 Lỗi cần sửa / issues ({len(issues)}):")
        for i in issues:
            print(f"  - {i}")
        print()
    else:
        print("✅ Hợp lệ / valid.")
    if args.catalog:
        print(f"Đã ghi type catalog: {args.catalog}")
    else:
        print("Xem trước type catalog / catalog preview:")
        for ln in catalog.splitlines():
            print(f"  {ln}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
