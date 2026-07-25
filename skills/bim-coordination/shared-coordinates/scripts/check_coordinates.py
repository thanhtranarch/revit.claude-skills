#!/usr/bin/env python3
"""
check_coordinates.py — So sánh toạ độ (Survey Point / góc true north) giữa các
                       model với một model chủ, bắt lệch/xoay.
                       Compare shared coordinates across models vs a reference,
                       flagging offsets and rotations.

Đầu vào: CSV mỗi dòng một model (model, sp_e, sp_n, sp_elev, angle, [reference]).
So mỗi model với model chủ theo dung sai; báo OK / OFFSET / ROTATED.
Chỉ dùng thư viện chuẩn.

Usage:
    python check_coordinates.py coords.csv
    python check_coordinates.py coords.csv --reference AR --tol 1.0 --angle-tol 0.01
Exit: 0 = tất cả khớp, 1 = có lệch, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

CANON = ["model", "sp_e", "sp_n", "sp_elev", "angle", "reference"]
ALIASES = {
    "model": "model", "name": "model", "file": "model", "discipline": "model", "model name": "model",
    "sp_e": "sp_e", "sp e": "sp_e", "easting": "sp_e", "east": "sp_e", "e": "sp_e",
    "survey e": "sp_e", "survey easting": "sp_e", "x": "sp_e",
    "sp_n": "sp_n", "sp n": "sp_n", "northing": "sp_n", "north": "sp_n", "n": "sp_n",
    "survey n": "sp_n", "survey northing": "sp_n", "y": "sp_n",
    "sp_elev": "sp_elev", "elevation": "sp_elev", "elev": "sp_elev", "z": "sp_elev", "level": "sp_elev",
    "angle": "angle", "angle to true north": "angle", "true north": "angle",
    "north angle": "angle", "rotation": "angle", "bearing": "angle",
    "reference": "reference", "is_reference": "reference", "master": "reference", "base": "reference",
}
TRUE = {"yes", "y", "true", "1", "x", "ref", "reference", "master", "có"}


def parse_num(s: str):
    s = (s or "").strip().replace(",", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
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


def pick_reference(models: list[dict], name: str | None) -> dict | None:
    if name:
        for m in models:
            if m["model"].strip().lower() == name.strip().lower():
                return m
        return None
    for m in models:
        if m["reference"].strip().lower() in TRUE:
            return m
    return models[0] if models else None


def delta(a: str, b: str):
    na, nb = parse_num(a), parse_num(b)
    if na is None or nb is None:
        return None
    return na - nb


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Compare shared coordinates across models.")
    ap.add_argument("csv", help="CSV toạ độ model")
    ap.add_argument("--reference", help="Tên model chủ (mặc định: cột reference hoặc dòng đầu)")
    ap.add_argument("--tol", type=float, default=1.0, help="Dung sai tuyến tính E/N/Elev (mặc định 1.0)")
    ap.add_argument("--angle-tol", type=float, default=0.01, help="Dung sai góc, độ (mặc định 0.01)")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2
    models = read_models(path)
    if not models:
        print("Không có model nào.", file=sys.stderr)
        return 2

    ref = pick_reference(models, args.reference)
    if ref is None:
        print(f"ERROR: không tìm thấy model chủ '{args.reference}'", file=sys.stderr)
        return 2

    print(f"Shared coordinates check — model chủ / reference: {ref['model'] or '(row 1)'}")
    print(f"Dung sai / tolerance: {args.tol} (E/N/Elev), {args.angle_tol}° (angle)")
    print(f"Ref: E={ref['sp_e']} N={ref['sp_n']} Elev={ref['sp_elev']} angle={ref['angle']}")
    print("-" * 72)

    n_bad = 0
    for m in models:
        if m is ref:
            print(f"{'REF':8}{m['model']}")
            continue
        de = delta(m["sp_e"], ref["sp_e"])
        dn = delta(m["sp_n"], ref["sp_n"])
        dz = delta(m["sp_elev"], ref["sp_elev"])
        da = delta(m["angle"], ref["angle"])
        tags = []
        if de is not None and abs(de) > args.tol:
            tags.append(f"ΔE={de:+.3f}")
        if dn is not None and abs(dn) > args.tol:
            tags.append(f"ΔN={dn:+.3f}")
        if dz is not None and abs(dz) > args.tol:
            tags.append(f"ΔElev={dz:+.3f}")
        rotated = da is not None and abs(da) > args.angle_tol
        if rotated:
            tags.append(f"Δangle={da:+.4f}°")
        missing = [f for f in ("sp_e", "sp_n", "sp_elev", "angle")
                   if parse_num(m[f]) is None]
        if missing:
            tags.append(f"thiếu/missing {','.join(missing)}")
        if tags:
            n_bad += 1
            kind = "ROTATED" if (rotated and len(tags) == 1) else "OFFSET"
            print(f"{kind:8}{m['model']}  ->  {', '.join(tags)}")
        else:
            print(f"{'OK':8}{m['model']}")

    print("-" * 72)
    print(f"{'⛔' if n_bad else '✅'} {n_bad} model lệch / mismatched "
          f"trên tổng {len(models) - 1} so sánh.")
    if n_bad:
        print("→ Kiểm tra model dùng Acquire Coordinates đúng chủ chưa, và true/project "
              "north có đồng bộ không (xem checklist trong SKILL.md).")
    return 1 if n_bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
