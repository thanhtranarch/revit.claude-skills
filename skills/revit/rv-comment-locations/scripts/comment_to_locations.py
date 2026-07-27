#!/usr/bin/env python3
"""
comment_to_locations.py — Comment/markup/RFI → punch list "vị trí cần update".
                          Turn review comments into a model update punch list.

Đọc export comment (Bluebeam markup summary, ACC/BIM360 issues, RFI register…),
trích **vị trí cần cập nhật trong model** — ưu tiên cột chuyên dụng (sheet, level,
grid, room, element id), nếu trống thì **phân tích text comment** (song ngữ EN/VI)
— rồi xuất punch list sắp theo ưu tiên + trạng thái.
Extracts model update locations from review comments (dedicated columns first,
then parsed from comment text) into a prioritized punch list.

Chỉ dùng thư viện chuẩn.

Usage:
    python comment_to_locations.py comments.csv
    python comment_to_locations.py comments.csv --csv out/punchlist.csv --json
    python comment_to_locations.py comments.csv --text-col Comment --sheet-col "Page Label"
Exit: 0 = OK, 2 = usage error.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

# --- Dò cột / column aliases ------------------------------------------------
ALIASES = {
    "id": ["id", "no", "no.", "index", "markup id", "issue id", "rfi no"],
    "subject": ["subject", "title", "type", "category"],
    "text": ["comment", "comments", "description", "note", "notes", "detail",
             "details", "body", "message", "response"],
    "sheet": ["sheet", "sheet number", "page label", "page", "drawing", "sheet no"],
    "level": ["level", "floor", "storey", "story", "tầng"],
    "grid": ["grid", "gridline", "axis", "trục"],
    "room": ["room", "space", "phòng"],
    "element_id": ["element id", "elementid", "elem id", "element", "revit id"],
    "author": ["author", "created by", "assignee", "owner", "raised by", "người"],
    "priority": ["priority", "severity", "importance", "mức độ", "ưu tiên"],
    "status": ["status", "state", "trạng thái"],
}

# --- Mẫu trích vị trí từ text (EN/VI) / location patterns in free text ------
RE_GRID = re.compile(
    r"(?:grid(?:line)?s?|axis|trục)\s*[:\-]?\s*"
    r"([A-Z]{1,2}\s?[-/~]\s?\d{1,2}|\d{1,2}\s?[-/~]\s?[A-Z]{1,2}|[A-Z]{1,2}\s?\d{1,2})",
    re.I)
RE_LEVEL = re.compile(
    r"(?:level|lvl|floor|storey|story|tầng)\s*[:\-]?\s*"
    r"(GF|RF|B\d|L\d{1,2}|\d{1,2}[A-Z]?)",
    re.I)
RE_ROOM = re.compile(r"(?:room|rm|space|phòng)\s*[:\-]?\s*([A-Z]?\d{1,4}[A-Z]?)", re.I)
RE_ELEM = re.compile(r"(?:element\s*id|elem(?:ent)?\s*id|element|revit\s*id|id|mã phần tử)"
                     r"\s*[:#\-]?\s*(\d{5,})", re.I)
RE_SHEET = re.compile(r"\b([A-Z]{1,3}-\d{2,4})\b")

PRIORITY_RANK = {"high": 0, "cao": 0, "critical": 0, "urgent": 0,
                 "medium": 1, "med": 1, "trung bình": 1, "normal": 1,
                 "low": 2, "thấp": 2, "minor": 2}


def autodetect(headers: list[str]) -> dict:
    lower = {h.lower().strip(): h for h in headers}
    found = {}
    for key, cands in ALIASES.items():
        for c in cands:
            if c in lower:
                found[key] = lower[c]
                break
    return found


def parse_from_text(text: str) -> dict:
    """Trích các phần vị trí từ text tự do."""
    out = {}
    for key, rx in (("grid", RE_GRID), ("level", RE_LEVEL),
                    ("room", RE_ROOM), ("element_id", RE_ELEM)):
        m = rx.search(text)
        if m:
            out[key] = re.sub(r"\s+", "", m.group(1)).upper()
    return out


def build_record(row: dict, cols: dict) -> dict:
    def col(key):
        return (row.get(cols[key]) or "").strip() if key in cols else ""

    rec = {
        "id": col("id"),
        "subject": col("subject"),
        "text": col("text"),
        "sheet": col("sheet"),
        "level": col("level"),
        "grid": col("grid"),
        "room": col("room"),
        "element_id": col("element_id"),
        "author": col("author"),
        "priority": col("priority"),
        "status": col("status"),
    }

    # phần vị trí có sẵn từ cột chuyên dụng
    loc_keys = ["sheet", "level", "grid", "room", "element_id"]
    from_column = any(rec[k] for k in loc_keys)

    # phân tích text để lấp phần còn thiếu
    blob = " ".join(x for x in (rec["subject"], rec["text"]) if x)
    parsed = parse_from_text(blob)
    filled_from_text = False
    for k, v in parsed.items():
        if not rec[k]:
            rec[k] = v
            filled_from_text = True
    # sheet: nếu chưa có cột & chưa có, thử text
    if not rec["sheet"]:
        m = RE_SHEET.search(blob)
        if m:
            rec["sheet"] = m.group(1).upper()
            filled_from_text = True

    has_loc = any(rec[k] for k in loc_keys)
    if not has_loc:
        rec["location_source"] = "none"
    elif from_column and filled_from_text:
        rec["location_source"] = "column+parsed"
    elif from_column:
        rec["location_source"] = "column"
    else:
        rec["location_source"] = "parsed"
    rec["location"] = " · ".join(
        f"{lbl}={rec[k]}" for k, lbl in
        (("sheet", "Sheet"), ("level", "Level"), ("grid", "Grid"),
         ("room", "Room"), ("element_id", "ElemID")) if rec[k]
    ) or "(chưa xác định / unresolved)"
    return rec


def prio_rank(rec: dict) -> int:
    return PRIORITY_RANK.get(rec["priority"].lower(), 3)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Comments → model update punch list.")
    ap.add_argument("input", help="CSV comment/markup/issue export")
    ap.add_argument("--text-col")
    ap.add_argument("--sheet-col")
    ap.add_argument("--level-col")
    ap.add_argument("--priority-col")
    ap.add_argument("--status-col")
    ap.add_argument("--open-only", action="store_true",
                    help="Chỉ giữ comment chưa đóng (status != closed/resolved)")
    ap.add_argument("--csv", dest="csv_out", help="Ghi punch list ra CSV")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    path = Path(args.input)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.input}", file=sys.stderr)
        return 2

    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        cols = autodetect(headers)
        for k, v in (("text", args.text_col), ("sheet", args.sheet_col),
                     ("level", args.level_col), ("priority", args.priority_col),
                     ("status", args.status_col)):
            if v:
                cols[k] = v
        if "text" not in cols and "subject" not in cols:
            print(f"ERROR: không dò được cột nội dung comment trong {headers}. "
                  f"Dùng --text-col.", file=sys.stderr)
            return 2
        records = [build_record(row, cols) for row in reader]

    if args.open_only:
        records = [r for r in records
                   if r["status"].lower() not in ("closed", "resolved", "done",
                                                   "đã đóng", "hoàn thành")]
    records.sort(key=lambda r: (prio_rank(r), r["location_source"] == "none"))

    total = len(records)
    resolved = sum(1 for r in records if r["location_source"] != "none")
    by_source = {}
    by_sheet = {}
    for r in records:
        by_source[r["location_source"]] = by_source.get(r["location_source"], 0) + 1
        key = r["sheet"] or "(no sheet)"
        by_sheet[key] = by_sheet.get(key, 0) + 1

    if args.json:
        print(json.dumps({
            "total": total,
            "with_location": resolved,
            "by_source": by_source,
            "by_sheet": by_sheet,
            "punchlist": records,
        }, ensure_ascii=False, indent=2))
    else:
        print(f"Comment → punch list vị trí cần update — {path.name}")
        print(f"Tổng comment: {total}  |  xác định được vị trí: {resolved} "
              f"({round(100*resolved/total,1) if total else 0}%)")
        print("Nguồn vị trí / source: " +
              ", ".join(f"{k}={v}" for k, v in by_source.items()))
        print("\nPunch list (sắp theo ưu tiên):")
        print(f"  {'#':<4}{'PRIO':<8}{'STATUS':<10}{'LOCATION':<40}COMMENT")
        for r in records:
            cid = r["id"] or "-"
            prio = r["priority"] or "-"
            stat = r["status"] or "-"
            note = (r["text"] or r["subject"])[:50]
            print(f"  {cid:<4}{prio:<8}{stat:<10}{r['location'][:38]:<40}{note}")
        unresolved = total - resolved
        if unresolved:
            print(f"\n⚠ {unresolved} comment CHƯA xác định được vị trí — cần bổ sung "
                  f"cột sheet/level/grid hoặc ghi rõ vị trí trong comment.")

    if args.csv_out:
        fields = ["id", "priority", "status", "sheet", "level", "grid", "room",
                  "element_id", "location_source", "author", "subject", "text"]
        with open(args.csv_out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(records)
        print(f"\nĐã ghi punch list → {args.csv_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
