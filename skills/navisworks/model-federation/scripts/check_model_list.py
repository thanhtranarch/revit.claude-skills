#!/usr/bin/env python3
"""
check_model_list.py — Kiểm tra danh sách model trước khi federate & clash.
                      Check a model register for clash-readiness before federating.

Đầu vào: CSV danh sách model (file, discipline, coord_system, units, last_updated).
Bắt: đơn vị/hệ toạ độ không đồng nhất, thiếu thông tin, model cũ (stale). Đưa ra
verdict READY / NOT READY. Chỉ dùng thư viện chuẩn.

Usage:
    python check_model_list.py models.csv
    python check_model_list.py models.csv --as-of 2026-07-24 --stale-days 7
Exit: 0 = READY, 1 = NOT READY, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

CANON = ["file", "discipline", "coord_system", "units", "last_updated", "status"]
ALIASES = {
    "file": "file", "model": "file", "file name": "file", "filename": "file", "model name": "file",
    "discipline": "discipline", "trade": "discipline", "category": "discipline", "type": "discipline",
    "coord system": "coord_system", "coordinate system": "coord_system",
    "coordinates": "coord_system", "coord": "coord_system", "shared coordinates": "coord_system",
    "units": "units", "unit": "units", "project units": "units",
    "last updated": "last_updated", "updated": "last_updated", "date": "last_updated",
    "last modified": "last_updated", "modified": "last_updated", "last sync": "last_updated",
    "status": "status", "state": "status", "publish status": "status",
}
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


def normalize_row(row: dict) -> dict:
    out = {c: "" for c in CANON}
    for k, v in row.items():
        if k is None:
            continue
        canon = ALIASES.get(k.strip().lower())
        if canon and not out[canon]:
            out[canon] = (v or "").strip()
    return out


def read_models(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return [normalize_row(r) for r in csv.DictReader(fh)]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Check a model list for clash-readiness.")
    ap.add_argument("csv", help="CSV danh sách model")
    ap.add_argument("--as-of", help="Mốc so ngày YYYY-MM-DD (mặc định hôm nay)")
    ap.add_argument("--stale-days", type=int, default=7,
                    help="Số ngày coi là cũ/stale (mặc định 7)")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2
    as_of = parse_date(args.as_of) or date.today()
    models = read_models(path)
    if not models:
        print("Không có model nào trong danh sách.", file=sys.stderr)
        return 2

    reds: list[str] = []
    warns: list[str] = []

    print(f"Model federation readiness — mốc / as of: {as_of.isoformat()}")
    print(f"Số model / models: {len(models)}")
    disciplines = [m["discipline"] or "(blank)" for m in models]
    print(f"Bộ môn / disciplines: {', '.join(f'{k}×{v}' for k, v in Counter(disciplines).most_common())}")
    print()

    # đơn vị / units consistency
    units = {m["units"].lower() for m in models if m["units"]}
    if len(units) > 1:
        reds.append(f"Đơn vị không đồng nhất / mixed units: {sorted(units)}")
    missing_units = [m["file"] for m in models if not m["units"]]
    if missing_units:
        warns.append(f"Thiếu đơn vị / missing units: {missing_units}")

    # hệ toạ độ / coordinate system consistency
    coords = {m["coord_system"].lower() for m in models if m["coord_system"]}
    if len(coords) > 1:
        reds.append(f"Hệ toạ độ không đồng nhất / mixed coordinate systems: {sorted(coords)}")
    missing_coord = [m["file"] for m in models if not m["coord_system"]]
    if missing_coord:
        reds.append(f"Thiếu hệ toạ độ / missing coordinate system: {missing_coord}")

    # model cũ / stale
    for m in models:
        d = parse_date(m["last_updated"])
        if d is None:
            warns.append(f"Thiếu/không đọc được ngày cập nhật / missing update date: {m['file']}")
        elif (as_of - d).days > args.stale_days:
            warns.append(f"Model cũ >{args.stale_days} ngày / stale: {m['file']} "
                         f"(cập nhật {m['last_updated']}, {(as_of - d).days}d)")

    for r in reds:
        print(f"🔴 {r}")
    for w in warns:
        print(f"🟡 {w}")

    ready = not reds
    print()
    print(f"Verdict: {'✅ READY' if ready else '⛔ NOT READY'}  "
          f"(🔴 {len(reds)}  🟡 {len(warns)})")
    if not ready:
        print("→ Xử lý các mục 🔴 (đồng nhất đơn vị & shared coordinates) trước khi clash.")
    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
