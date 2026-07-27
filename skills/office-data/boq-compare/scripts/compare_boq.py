#!/usr/bin/env python3
"""
compare_boq.py — So sánh hai bản BoQ / bảng khối lượng (v1 vs v2).
                 Diff two bills of quantities / takeoffs (old vs new).

Ghép theo mã item (hoặc mô tả) và báo: item thêm/bớt, và khối lượng tăng/giảm
kèm Δ và %. Nếu có cột amount thì báo cả biến động giá trị. Chỉ dùng thư viện
chuẩn.
Keys rows by item code (or description) and reports added/removed items and
quantity increases/decreases with delta and %. Stdlib only.

Usage:
    python compare_boq.py old.csv new.csv
    python compare_boq.py old.csv new.csv --key "Item" --csv out/boq_diff.csv
Exit: 0 = ok, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

CODE_ALIASES = ["code", "item", "item code", "item no", "ref", "boq ref", "sor", "no"]
DESC_ALIASES = ["description", "desc", "item description", "work", "particulars", "name"]
QTY_ALIASES = ["quantity", "qty", "quantities"]
UNIT_ALIASES = ["unit", "uom", "units"]
AMOUNT_ALIASES = ["amount", "total", "value", "cost"]


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


def read_boq(path: Path, key_pref: str | None):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        key_col = key_pref or find_col(headers, CODE_ALIASES) or find_col(headers, DESC_ALIASES)
        if not key_col:
            print(f"ERROR: không dò được cột khoá (mã/mô tả) trong {headers}. Dùng --key.",
                  file=sys.stderr)
            sys.exit(2)
        qty_col = find_col(headers, QTY_ALIASES)
        unit_col = find_col(headers, UNIT_ALIASES)
        amt_col = find_col(headers, AMOUNT_ALIASES)
        desc_col = find_col(headers, DESC_ALIASES)
        data: dict[str, dict] = {}
        dups = 0
        for r in reader:
            key = (r.get(key_col) or "").strip()
            if not key:
                continue
            if key in data:
                dups += 1
            data[key] = {
                "qty": parse_num(r.get(qty_col)) if qty_col else None,
                "unit": (r.get(unit_col) or "").strip() if unit_col else "",
                "amount": parse_num(r.get(amt_col)) if amt_col else None,
                "desc": (r.get(desc_col) or "").strip() if desc_col else "",
            }
    return data, key_col, dups, amt_col is not None


def q(v):
    return 0.0 if v is None else v


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Diff two bills of quantities / takeoffs.")
    ap.add_argument("old", help="BoQ cũ / old CSV")
    ap.add_argument("new", help="BoQ mới / new CSV")
    ap.add_argument("--key", help="Tên cột khoá (mặc định tự dò mã→mô tả)")
    ap.add_argument("--csv", dest="out_csv", help="Ghi diff ra CSV")
    args = ap.parse_args(argv)

    op, npath = Path(args.old), Path(args.new)
    for p in (op, npath):
        if not p.is_file():
            print(f"ERROR: không tìm thấy: {p}", file=sys.stderr)
            return 2

    old, key_col, old_dup, old_amt = read_boq(op, args.key)
    new, _, new_dup, new_amt = read_boq(npath, args.key)
    has_amount = old_amt and new_amt

    old_k, new_k = set(old), set(new)
    added = sorted(new_k - old_k)
    removed = sorted(old_k - new_k)
    changed = []
    for k in sorted(old_k & new_k):
        oq, nq = q(old[k]["qty"]), q(new[k]["qty"])
        oa, na = q(old[k]["amount"]), q(new[k]["amount"])
        if round(oq, 4) != round(nq, 4) or (has_amount and round(oa, 4) != round(na, 4)):
            changed.append(k)

    print(f"BoQ compare:  cũ/old={len(old)}  mới/new={len(new)}  (khoá/key: {key_col})")
    if old_dup or new_dup:
        print(f"  ⚠ khoá trùng bị gộp / duplicate keys collapsed: old={old_dup}, new={new_dup}")
    print(f"  + Thêm / Added:        {len(added)}")
    print(f"  − Bớt / Removed:       {len(removed)}")
    print(f"  ~ Đổi khối lượng / Qty or value changed: {len(changed)}")
    print()

    if added:
        print(f"+ Thêm / Added ({len(added)}):")
        for k in added:
            it = new[k]
            print(f"  {k}  {it['desc']}  →  {q(it['qty']):,.2f} {it['unit']}".rstrip())
        print()
    if removed:
        print(f"− Bớt / Removed ({len(removed)}):")
        for k in removed:
            it = old[k]
            print(f"  {k}  {it['desc']}  →  {q(it['qty']):,.2f} {it['unit']}".rstrip())
        print()
    if changed:
        print(f"~ Đổi / Changed ({len(changed)}):")
        for k in changed:
            oq, nq = q(old[k]["qty"]), q(new[k]["qty"])
            d = nq - oq
            pct = f"{d / oq * 100:+.1f}%" if oq else "n/a"
            print(f"  {k}  {new[k]['desc'] or old[k]['desc']}: "
                  f"{oq:,.2f} → {nq:,.2f} {new[k]['unit']} (Δ {d:+,.2f}, {pct})")
        print()

    if has_amount:
        old_total = sum(q(v["amount"]) for v in old.values())
        new_total = sum(q(v["amount"]) for v in new.values())
        d = new_total - old_total
        pct = f"{d / old_total * 100:+.1f}%" if old_total else "n/a"
        print(f"Tổng giá trị / Total amount: {old_total:,.2f} → {new_total:,.2f} "
              f"(Δ {d:+,.2f}, {pct})")

    if args.out_csv:
        out = Path(args.out_csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["key", "change", "description", "old_qty", "new_qty", "delta", "unit"])
            for k in added:
                w.writerow([k, "added", new[k]["desc"], "", q(new[k]["qty"]), q(new[k]["qty"]), new[k]["unit"]])
            for k in removed:
                w.writerow([k, "removed", old[k]["desc"], q(old[k]["qty"]), "", -q(old[k]["qty"]), old[k]["unit"]])
            for k in changed:
                oq, nq = q(old[k]["qty"]), q(new[k]["qty"])
                w.writerow([k, "changed", new[k]["desc"] or old[k]["desc"], oq, nq, nq - oq, new[k]["unit"]])
        print(f"\nĐã ghi diff / wrote diff: {args.out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
