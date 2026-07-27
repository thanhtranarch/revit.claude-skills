#!/usr/bin/env python3
"""
compare_models.py — So sánh hai bản export element của model (v1 vs v2).
                    Diff two Revit element exports (old vs new snapshot).

Ghép theo Element ID/GUID rồi báo cáo: thêm mới / xoá / thay đổi (kèm trường
nào đổi từ gì → gì). Hữu ích khi QA giữa hai lần phát hành hoặc kiểm tra thay
đổi giữa các vòng coordination. Chỉ dùng thư viện chuẩn.
Keys rows by Element ID/GUID and reports added / deleted / changed (with the
fields that changed old → new). Stdlib only.

Usage:
    python compare_models.py old.csv new.csv
    python compare_models.py old.csv new.csv --compare-cols Type,Level --csv out/diff.csv
Exit: 0 = ok, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

ID_ALIASES = ["element id", "elementid", "id", "guid", "unique id",
              "uniqueid", "ifc guid", "ifcguid"]
CATEGORY_ALIASES = ["category", "cat", "revit category"]


def find_col(headers: list[str], aliases: list[str]):
    low = {h.strip().lower(): h for h in headers}
    for a in aliases:
        if a in low:
            return low[a]
    return None


def read_keyed(path: Path, id_pref: str | None):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        id_col = id_pref or find_col(headers, ID_ALIASES)
        if not id_col:
            print(f"ERROR: không dò được cột ID trong {headers}. Dùng --id-col.",
                  file=sys.stderr)
            sys.exit(2)
        data: dict[str, dict] = {}
        dups = 0
        for r in reader:
            key = (r.get(id_col) or "").strip()
            if not key:
                continue
            if key in data:
                dups += 1
            data[key] = r
    return data, headers, id_col, dups


def cell(row: dict, col: str) -> str:
    return (row.get(col) or "").strip()


def category_breakdown(ids: set, source: dict, cat_col: str | None) -> str:
    if not cat_col or not ids:
        return ""
    c = Counter(cell(source[i], cat_col) or "(blank)" for i in ids)
    return "  (" + ", ".join(f"{v} {k}" for k, v in c.most_common()) + ")"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Diff two Revit element exports.")
    ap.add_argument("old", help="CSV export cũ / old snapshot")
    ap.add_argument("new", help="CSV export mới / new snapshot")
    ap.add_argument("--id-col", help="Tên cột ID (mặc định tự dò)")
    ap.add_argument("--compare-cols", help="Danh sách cột so sánh, phân tách bằng dấu phẩy")
    ap.add_argument("--csv", dest="out_csv", help="Ghi diff ra CSV (id,change,field,old,new)")
    ap.add_argument("--limit", type=int, default=50, help="Giới hạn số dòng liệt kê (mặc định 50)")
    args = ap.parse_args(argv)

    op, np_ = Path(args.old), Path(args.new)
    for p in (op, np_):
        if not p.is_file():
            print(f"ERROR: không tìm thấy: {p}", file=sys.stderr)
            return 2

    old, old_h, old_id, old_dup = read_keyed(op, args.id_col)
    new, new_h, new_id, new_dup = read_keyed(np_, args.id_col)

    if args.compare_cols:
        compare_cols = [c.strip() for c in args.compare_cols.split(",") if c.strip()]
    else:
        common = [h for h in new_h if h in set(old_h)]
        compare_cols = [h for h in common if h not in (old_id, new_id)]
    cat_col = find_col(new_h, CATEGORY_ALIASES)

    old_ids, new_ids = set(old), set(new)
    added = new_ids - old_ids
    deleted = old_ids - new_ids
    common_ids = old_ids & new_ids

    changed: dict[str, list[tuple[str, str, str]]] = {}
    for i in common_ids:
        diffs = [(c, cell(old[i], c), cell(new[i], c))
                 for c in compare_cols if cell(old[i], c) != cell(new[i], c)]
        if diffs:
            changed[i] = diffs

    print(f"So sánh model / model diff:  cũ/old={len(old)}  mới/new={len(new)}  "
          f"(cột so sánh / compare cols: {', '.join(compare_cols) or '—'})")
    if old_dup or new_dup:
        print(f"  ⚠ ID trùng bị gộp (giữ dòng cuối) / duplicate IDs collapsed: "
              f"old={old_dup}, new={new_dup}")
    print(f"  + Thêm mới / Added:   {len(added)}{category_breakdown(added, new, cat_col)}")
    print(f"  − Xoá / Deleted:      {len(deleted)}{category_breakdown(deleted, old, cat_col)}")
    print(f"  ~ Thay đổi / Changed: {len(changed)}")
    print()

    def show(title, ids, source):
        if not ids:
            return
        print(f"{title} ({len(ids)}):")
        for i in sorted(ids)[:args.limit]:
            cat = f"[{cell(source[i], cat_col)}] " if cat_col else ""
            print(f"  {i}  {cat}".rstrip())
        if len(ids) > args.limit:
            print(f"  … +{len(ids) - args.limit} nữa / more")
        print()

    show("+ Thêm mới / Added", added, new)
    show("− Xoá / Deleted", deleted, old)
    if changed:
        print(f"~ Thay đổi / Changed ({len(changed)}):")
        for i in sorted(changed)[:args.limit]:
            for field, ov, nv in changed[i]:
                print(f"  {i}  {field}: '{ov}' → '{nv}'")
        if len(changed) > args.limit:
            print(f"  … +{len(changed) - args.limit} nữa / more")
        print()

    if args.out_csv:
        out = Path(args.out_csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["id", "change", "field", "old", "new"])
            for i in sorted(added):
                w.writerow([i, "added", "", "", cell(new[i], cat_col) if cat_col else ""])
            for i in sorted(deleted):
                w.writerow([i, "deleted", "", cell(old[i], cat_col) if cat_col else "", ""])
            for i in sorted(changed):
                for field, ov, nv in changed[i]:
                    w.writerow([i, "changed", field, ov, nv])
        print(f"Đã ghi diff / wrote diff: {args.out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
