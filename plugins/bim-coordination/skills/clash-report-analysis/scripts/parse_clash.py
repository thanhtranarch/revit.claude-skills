#!/usr/bin/env python3
"""
parse_clash.py — Phân tích báo cáo clash XML của Navisworks Clash Detective.
                 Parse a Navisworks Clash Detective XML report.

Chỉ dùng thư viện chuẩn (xml.etree). / Stdlib only.

Usage:
    python parse_clash.py report.xml
    python parse_clash.py report.xml --csv register.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


def _text(el, path, default=""):
    child = el.find(path)
    return child.text.strip() if child is not None and child.text else default


def parse(xml_path: Path) -> list[dict]:
    """Trả về danh sách clash dạng dict. / Return a list of clash dicts."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    rows: list[dict] = []

    # Navisworks: batchtest > clashtests > clashtest > clashresults > clashresult
    for test in root.iter("clashtest"):
        test_name = test.get("name", "Unnamed test")
        for res in test.iter("clashresult"):
            objects = []
            for obj in res.iter("clashobject"):
                # tên item lấy từ smarttags hoặc pathlink/nodes
                name = _text(obj, "smarttags/smarttag/value")
                if not name:
                    name = obj.get("name", "")
                objects.append(name or "?")
            item_a = objects[0] if len(objects) > 0 else ""
            item_b = objects[1] if len(objects) > 1 else ""
            rows.append({
                "name": res.get("name", ""),
                "test": test_name,
                "status": res.get("status", "").capitalize() or "Unknown",
                "distance": res.get("distance", ""),
                "grid": res.get("gridlocation", ""),
                "item_a": item_a,
                "item_b": item_b,
            })
    return rows


def summarize(rows: list[dict]) -> str:
    if not rows:
        return "Không tìm thấy clash nào trong report. / No clashes found."
    by_test = Counter(r["test"] for r in rows)
    by_status = Counter(r["status"] for r in rows)

    lines = [f"Tổng số clash / Total clashes: {len(rows)}", ""]
    lines.append("Theo trạng thái / By status:")
    for status, n in by_status.most_common():
        lines.append(f"  {status:12} {n:5}")
    lines.append("")
    lines.append("Theo clash test / By clash test:")
    for test, n in by_test.most_common():
        lines.append(f"  {n:5}  {test}")
    # Ưu tiên: clash New/Active
    active = [r for r in rows if r["status"] in ("New", "Active")]
    lines.append("")
    lines.append(f"Cần xử lý (New/Active) / To action: {len(active)}")
    return "\n".join(lines)


def write_csv(rows: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["name", "test", "status", "distance", "grid", "item_a", "item_b"]
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Parse Navisworks clash XML report.")
    ap.add_argument("xml", help="Đường dẫn file XML report")
    ap.add_argument("--csv", help="Xuất register ra CSV")
    args = ap.parse_args(argv)

    xml_path = Path(args.xml)
    if not xml_path.is_file():
        print(f"ERROR: không tìm thấy file: {xml_path}", file=sys.stderr)
        return 2
    try:
        rows = parse(xml_path)
    except ET.ParseError as exc:
        print(f"ERROR: XML không hợp lệ: {exc}", file=sys.stderr)
        return 2

    print(summarize(rows))
    if args.csv:
        write_csv(rows, Path(args.csv))
        print(f"\nĐã ghi register: {args.csv} ({len(rows)} dòng)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
