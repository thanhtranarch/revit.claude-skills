#!/usr/bin/env python3
"""
analyze_shared_params.py — Phân tích Revit shared parameter file (.txt).
                           Analyze a Revit shared parameter file.

Định dạng file là tab-delimited với các section GROUP và PARAM.
Chỉ dùng thư viện chuẩn. / Stdlib only.

Usage:
    python analyze_shared_params.py shared_params.txt
    python analyze_shared_params.py shared_params.txt --csv params.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Thứ tự cột chuẩn của dòng PARAM trong shared parameter file.
PARAM_FIELDS = ["guid", "name", "datatype", "datacategory", "group",
                "visible", "description", "usermodifiable", "hidewhennovalue"]


def parse(path: Path):
    groups: dict[str, str] = {}      # group id -> group name
    params: list[dict] = []
    with path.open(encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line or line.startswith("#") or line.startswith("*"):
                continue
            cols = line.split("\t")
            tag = cols[0]
            if tag == "GROUP" and len(cols) >= 3:
                groups[cols[1]] = cols[2]
            elif tag == "PARAM":
                vals = cols[1:]
                rec = {f: (vals[i] if i < len(vals) else "") for i, f in enumerate(PARAM_FIELDS)}
                params.append(rec)
    # gán tên group
    for p in params:
        p["group_name"] = groups.get(p["group"], f"(id {p['group']})")
    return groups, params


def analyze(groups, params) -> list[str]:
    lines = [f"Tổng số parameter / Total params: {len(params)}",
             f"Số group: {len(groups)}", ""]

    # theo group
    by_group = Counter(p["group_name"] for p in params)
    lines.append("Theo group / by group:")
    for g, n in by_group.most_common():
        lines.append(f"  {n:4}  {g}")
    lines.append("")

    # theo data type
    by_type = Counter(p["datatype"] or "(blank)" for p in params)
    lines.append("Theo data type / by data type:")
    for t, n in by_type.most_common():
        lines.append(f"  {n:4}  {t}")
    lines.append("")

    # --- vấn đề / issues ---
    issues: list[str] = []

    guid_map = defaultdict(list)
    for p in params:
        guid_map[p["guid"]].append(p["name"])
    for guid, names in guid_map.items():
        if len(names) > 1:
            issues.append(f"[DUPLICATE GUID] {guid} dùng cho: {', '.join(names)}")

    name_map = defaultdict(set)
    for p in params:
        name_map[p["name"].lower()].add(p["guid"])
    for name, guids in name_map.items():
        if len(guids) > 1:
            issues.append(f"[DUPLICATE NAME] '{name}' có {len(guids)} GUID khác nhau")

    missing_desc = [p["name"] for p in params if not p["description"].strip()]
    if missing_desc:
        issues.append(f"[MISSING DESCRIPTION] {len(missing_desc)} param thiếu mô tả: "
                      + ", ".join(missing_desc[:10]) + ("…" if len(missing_desc) > 10 else ""))

    lines.append(f"Vấn đề phát hiện / issues: {len(issues)}")
    for it in issues:
        lines.append(f"  {it}")
    if not issues:
        lines.append("  (không có — bộ parameter sạch)")
    return lines


def write_csv(params, out: Path):
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = PARAM_FIELDS + ["group_name"]
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(params)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Analyze a Revit shared parameter file.")
    ap.add_argument("txt")
    ap.add_argument("--csv")
    args = ap.parse_args(argv)

    path = Path(args.txt)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.txt}", file=sys.stderr)
        return 2

    groups, params = parse(path)
    if not params:
        print("Không tìm thấy dòng PARAM nào — file có đúng shared parameter file?",
              file=sys.stderr)
        return 2

    print("\n".join(analyze(groups, params)))
    if args.csv:
        write_csv(params, Path(args.csv))
        print(f"\nĐã ghi: {args.csv} ({len(params)} param)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
