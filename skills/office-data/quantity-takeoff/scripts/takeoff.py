#!/usr/bin/env python3
"""
takeoff.py — Bóc tách khối lượng từ schedule export (Revit/Excel).
             Aggregate a quantity takeoff from a schedule export.

Gom theo một cột nhóm (mặc định Category) và cộng các cột khối lượng phát hiện
được (count/area/volume/length/weight), bỏ đơn vị & dấu phẩy. Chỉ dùng thư
viện chuẩn.
Groups by a column (default Category) and sums detected quantity columns
(count/area/volume/length/weight), stripping units and commas. Stdlib only.

Usage:
    python takeoff.py schedule.csv
    python takeoff.py schedule.csv --group-by Type --csv out/takeoff.csv
Exit: 0 = ok, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

GROUP_ALIASES = ["category", "cat", "group", "family", "type",
                 "assembly", "element type", "family and type"]
# (khoá / key, nhãn / label, alias cột, số lẻ / decimals)
QTY_DEFS = [
    ("count", "Count", ["count", "qty", "quantity", "nos", "no.", "number", "pcs", "each"], 0),
    ("area", "Area", ["area", "gross area", "net area", "surface area", "floor area"], 2),
    ("volume", "Volume", ["volume", "gross volume", "net volume"], 2),
    ("length", "Length", ["length", "len", "perimeter", "run", "linear"], 2),
    ("weight", "Weight", ["weight", "mass"], 1),
]


def parse_num(s: str):
    s = re.sub(r"[^\d.\-]", "", (s or "").replace(",", ""))
    if s in ("", "-", ".", "-.", "--"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def find_col(headers: list[str], aliases: list[str]):
    low = {h.strip().lower(): h for h in headers}
    for a in aliases:
        if a in low:
            return low[a]
    return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Aggregate a quantity takeoff from a schedule export.")
    ap.add_argument("csv", help="CSV schedule export")
    ap.add_argument("--group-by", help="Tên cột nhóm (mặc định tự dò Category…)")
    ap.add_argument("--csv", dest="out_csv", help="Xuất bảng takeoff ra CSV")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2

    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        rows = list(reader)

    group_col = args.group_by or find_col(headers, GROUP_ALIASES) or (headers[0] if headers else None)
    if not group_col or group_col not in headers:
        print(f"ERROR: không dò được cột nhóm trong {headers}. Dùng --group-by.", file=sys.stderr)
        return 2

    qty_cols = [(key, label, find_col(headers, aliases), dec)
                for key, label, aliases, dec in QTY_DEFS]
    qty_cols = [(key, label, col, dec) for key, label, col, dec in qty_cols if col]
    has_count = any(key == "count" for key, _, _, _ in qty_cols)

    groups: dict[str, dict] = defaultdict(lambda: {"rows": 0, **{k: 0.0 for k, *_ in qty_cols}})
    for r in rows:
        g = (r.get(group_col) or "(blank)").strip() or "(blank)"
        groups[g]["rows"] += 1
        for key, _, col, _ in qty_cols:
            v = parse_num(r.get(col))
            if v is not None:
                groups[g][key] += v

    # bảng / table
    cols = [("rows", "Rows", 0)] + [(k, lbl, dec) for k, lbl, _, dec in qty_cols]
    widths = {k: max(len(lbl), 12) for k, lbl, _ in cols}
    header = f"{group_col[:28]:28}" + "".join(f"  {lbl:>{widths[k]}}" for k, lbl, _ in cols)
    print(header)
    print("-" * len(header))

    def fmt(v, dec):
        return f"{v:,.{dec}f}" if dec else f"{int(round(v)):,}"

    total = {k: 0.0 for k, *_ in cols}
    for g in sorted(groups, key=lambda x: -groups[x].get("count", groups[x]["rows"]) if has_count else -groups[x]["rows"]):
        line = f"{g[:28]:28}"
        for k, _, dec in cols:
            val = groups[g][k]
            total[k] += val
            line += f"  {fmt(val, dec):>{widths[k]}}"
        print(line)
    print("-" * len(header))
    tline = f"{'TỔNG / TOTAL':28}"
    for k, _, dec in cols:
        tline += f"  {fmt(total[k], dec):>{widths[k]}}"
    print(tline)
    print(f"\n{len(groups)} nhóm / groups, {len(rows)} dòng / rows.")

    if args.out_csv:
        out = Path(args.out_csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow([group_col] + [lbl for _, lbl, _ in cols])
            for g in sorted(groups):
                w.writerow([g] + [round(groups[g][k], dec) for k, _, dec in cols])
            w.writerow(["TOTAL"] + [round(total[k], dec) for k, _, dec in cols])
        print(f"Đã ghi takeoff / wrote takeoff: {args.out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
