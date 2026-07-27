#!/usr/bin/env python3
"""
parse_dxf.py — Đọc file DXF (ASCII), thống kê layer/đối tượng & xuất build plan.
               Parse a DXF (ASCII), inventory layers/entities & emit a build plan.

Giúp bước "dựng model từ hình vẽ": kiểm kê CAD import (line/polyline/circle/block/
text) theo layer, tính tổng chiều dài, gợi ý phần tử Revit theo tên layer, và
xuất JSON (segments + points) để template pyRevit/Dynamo tạo phần tử.
Chỉ dùng thư viện chuẩn. DXF phải là bản ASCII (không phải DXF nhị phân/DWG).

Usage:
    python parse_dxf.py plan.dxf
    python parse_dxf.py plan.dxf --json > plan.json
Exit: 0 = ok, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

GEOM_TYPES = ("LINE", "LWPOLYLINE", "POLYLINE", "CIRCLE", "ARC", "INSERT", "TEXT", "MTEXT")


def read_pairs(path: Path) -> list[tuple[int, str]]:
    raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
    pairs: list[tuple[int, str]] = []
    for i in range(0, len(raw) - 1, 2):
        code_s = raw[i].strip()
        try:
            code = int(code_s)
        except ValueError:
            continue
        pairs.append((code, raw[i + 1].strip()))
    return pairs


def parse_entities(pairs: list[tuple[int, str]]) -> list[dict]:
    section = None
    expect_name = False
    entities: list[dict] = []
    cur: dict | None = None
    for code, val in pairs:
        if code == 0:
            if cur is not None:
                entities.append(cur)
                cur = None
            if val == "SECTION":
                expect_name = True
            elif val == "ENDSEC":
                section = None
            elif val == "EOF":
                break
            elif section == "ENTITIES":
                cur = {"type": val, "codes": []}
        else:
            if expect_name and code == 2:
                section, expect_name = val, False
            elif cur is not None:
                cur["codes"].append((code, val))
    if cur is not None:
        entities.append(cur)
    return entities


def fvals(codes, code):
    out = []
    for c, v in codes:
        if c == code:
            try:
                out.append(float(v))
            except ValueError:
                pass
    return out


def first_str(codes, code, default=""):
    return next((v for c, v in codes if c == code), default)


def layer_of(codes):
    return first_str(codes, 8, "0")


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def segment_of(codes):
    """(x1,y1),(x2,y2) cho LINE, hoặc None."""
    xs1, ys1 = fvals(codes, 10), fvals(codes, 20)
    xs2, ys2 = fvals(codes, 11), fvals(codes, 21)
    if xs1 and ys1 and xs2 and ys2:
        return [[xs1[0], ys1[0]], [xs2[0], ys2[0]]]
    return None


def polyline_pts(codes):
    xs, ys = fvals(codes, 10), fvals(codes, 20)
    return list(zip(xs, ys))


def entity_length(ent) -> float:
    t, codes = ent["type"], ent["codes"]
    if t == "LINE":
        seg = segment_of(codes)
        return _dist(seg[0], seg[1]) if seg else 0.0
    if t in ("LWPOLYLINE", "POLYLINE"):
        pts = polyline_pts(codes)
        length = sum(_dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        closed = next((int(v) for c, v in codes if c == 70), 0) & 1
        if closed and len(pts) > 2:
            length += _dist(pts[-1], pts[0])
        return length
    if t == "CIRCLE":
        r = fvals(codes, 40)
        return 2 * math.pi * r[0] if r else 0.0
    return 0.0


def suggest_element(layer: str) -> str:
    l = layer.lower()
    rules = [
        (("wall", "tuong", "tường"), "Wall"),
        (("column", "col", "cot", "cột"), "Column"),
        (("beam", "dam", "dầm", "girder"), "Beam"),
        (("grid", "truc", "trục", "axis"), "Grid"),
        (("door", "cua di", "cửa"), "Door"),
        (("window", "cua so"), "Window"),
        (("room", "space", "phong", "phòng"), "Room"),
        (("dim", "text", "note", "annot"), "(annotation)"),
    ]
    for keys, elem in rules:
        if any(k in l for k in keys):
            return elem
    return "(review)"


def analyze(entities: list[dict]) -> dict:
    layers: dict[str, dict] = {}
    all_x: list[float] = []
    all_y: list[float] = []
    for ent in entities:
        codes = ent["codes"]
        lay = layer_of(codes)
        d = layers.setdefault(lay, {
            "counts": Counter(), "length": 0.0, "segments": [],
            "points": [], "blocks": Counter(), "texts": 0,
        })
        d["counts"][ent["type"]] += 1
        d["length"] += entity_length(ent)
        all_x.extend(fvals(codes, 10))
        all_y.extend(fvals(codes, 20))
        if ent["type"] == "LINE":
            seg = segment_of(codes)
            if seg:
                d["segments"].append(seg)
        if ent["type"] == "INSERT":
            xs, ys = fvals(codes, 10), fvals(codes, 20)
            if xs and ys:
                d["points"].append([xs[0], ys[0]])
            d["blocks"][first_str(codes, 2, "")] += 1
        if ent["type"] in ("TEXT", "MTEXT"):
            d["texts"] += 1
    bbox = None
    if all_x and all_y:
        bbox = [[min(all_x), min(all_y)], [max(all_x), max(all_y)]]
    return {"layers": layers, "bbox": bbox, "count": len(entities)}


def build_plan(result: dict) -> dict:
    layers = []
    for name, d in sorted(result["layers"].items()):
        layers.append({
            "layer": name,
            "suggested_element": suggest_element(name),
            "counts": dict(d["counts"]),
            "length": round(d["length"], 3),
            "segments": [[[round(x, 3), round(y, 3)] for x, y in seg] for seg in d["segments"]],
            "points": [[round(x, 3), round(y, 3)] for x, y in d["points"]],
            "blocks": dict(d["blocks"]),
        })
    return {"count": result["count"], "bbox": result["bbox"], "layers": layers}


def print_report(result: dict) -> None:
    print(f"DXF — {result['count']} entity, {len(result['layers'])} layer")
    hdr = f"{'Layer':18} {'Line':>5} {'Poly':>5} {'Circ':>5} {'Ins':>4} {'Txt':>4} " \
          f"{'Length':>12}  → gợi ý / suggest"
    print(hdr)
    print("-" * len(hdr))
    for name, d in sorted(result["layers"].items()):
        c = d["counts"]
        poly = c.get("LWPOLYLINE", 0) + c.get("POLYLINE", 0)
        print(f"{name[:18]:18} {c.get('LINE', 0):>5} {poly:>5} {c.get('CIRCLE', 0):>5} "
              f"{c.get('INSERT', 0):>4} {c.get('TEXT', 0) + c.get('MTEXT', 0):>4} "
              f"{d['length']:>12,.1f}  {suggest_element(name)}")
    if result["bbox"]:
        (x0, y0), (x1, y1) = result["bbox"]
        print(f"\nBounding box: ({x0:,.1f}, {y0:,.1f}) → ({x1:,.1f}, {y1:,.1f}) "
              f"[đơn vị bản vẽ / drawing units]")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Parse an ASCII DXF: layers, entities, build plan.")
    ap.add_argument("dxf", help="File DXF (ASCII)")
    ap.add_argument("--json", action="store_true", help="Xuất build plan JSON (segments/points)")
    args = ap.parse_args(argv)

    path = Path(args.dxf)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.dxf}", file=sys.stderr)
        return 2

    entities = parse_entities(read_pairs(path))
    if not entities:
        print("Không tìm thấy entity nào (DXF rỗng hoặc là DXF nhị phân/DWG).", file=sys.stderr)
        return 2
    result = analyze(entities)

    if args.json:
        print(json.dumps(build_plan(result), ensure_ascii=False, indent=2))
    else:
        print_report(result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
