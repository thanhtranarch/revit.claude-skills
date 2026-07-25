#!/usr/bin/env python3
"""
compare_markup.py — So sánh markup/annotation & text giữa 2 bản PDF.
                    Compare annotations & text between two PDF revisions.

Dùng pypdf. / Requires pypdf (pip install pypdf).

Usage:
    python compare_markup.py old.pdf new.pdf
    python compare_markup.py old.pdf new.pdf --csv diff.csv
"""
from __future__ import annotations

import argparse
import csv
import difflib
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    print("ERROR: cần pypdf — chạy: pip install pypdf", file=sys.stderr)
    sys.exit(2)

# khoảng cách toạ độ (points) coi là "cùng vị trí" khi ghép cặp markup
MOVE_TOLERANCE = 5.0


def extract_annots(reader: PdfReader) -> list[dict]:
    """Lấy annotation của từng trang. / Extract annotations per page."""
    out: list[dict] = []
    for pno, page in enumerate(reader.pages, 1):
        annots = page.get("/Annots")
        if not annots:
            continue
        for ref in annots:
            try:
                obj = ref.get_object()
            except Exception:
                continue
            subtype = str(obj.get("/Subtype", "")).lstrip("/")
            if subtype in ("Link", "Popup"):
                continue  # không phải markup review
            contents = obj.get("/Contents")
            rect = obj.get("/Rect") or [0, 0, 0, 0]
            try:
                x, y = float(rect[0]), float(rect[1])
            except (TypeError, ValueError):
                x, y = 0.0, 0.0
            out.append({
                "page": pno,
                "subtype": subtype or "Unknown",
                "content": (str(contents).strip() if contents else ""),
                "x": round(x, 1),
                "y": round(y, 1),
            })
    return out


def _key(a: dict) -> tuple:
    return (a["page"], a["subtype"], a["content"])


def diff_annots(old: list[dict], new: list[dict]) -> list[dict]:
    """Ghép cặp theo (page, subtype, content); phân loại added/removed/moved."""
    changes: list[dict] = []
    old_by_key: dict[tuple, list[dict]] = {}
    for a in old:
        old_by_key.setdefault(_key(a), []).append(a)

    matched_old = set()
    for a in new:
        k = _key(a)
        candidates = old_by_key.get(k, [])
        match = None
        for idx, cand in enumerate(candidates):
            cid = id(cand)
            if cid in matched_old:
                continue
            match = (idx, cand)
            break
        if match is None:
            changes.append({**a, "change": "added"})
        else:
            _, cand = match
            matched_old.add(id(cand))
            moved = abs(cand["x"] - a["x"]) > MOVE_TOLERANCE or abs(cand["y"] - a["y"]) > MOVE_TOLERANCE
            if moved:
                changes.append({**a, "change": "moved",
                                "from": f"({cand['x']},{cand['y']})",
                                "to": f"({a['x']},{a['y']})"})
    for a in old:
        if id(a) not in matched_old and _key(a) in {_key(x) for x in old}:
            # chỉ báo removed nếu không có bản new tương ứng
            pass
    # removed = old chưa được ghép
    for a in old:
        if id(a) not in matched_old:
            changes.append({**a, "change": "removed"})
    return changes


def page_text(reader: PdfReader) -> list[str]:
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            texts.append("")
    return texts


def text_diff_summary(old: PdfReader, new: PdfReader) -> list[str]:
    lines = []
    ot, nt = page_text(old), page_text(new)
    for i in range(max(len(ot), len(nt))):
        o = (ot[i] if i < len(ot) else "").splitlines()
        n = (nt[i] if i < len(nt) else "").splitlines()
        d = list(difflib.unified_diff(o, n, lineterm="", n=0))
        adds = sum(1 for x in d if x.startswith("+") and not x.startswith("+++"))
        dels = sum(1 for x in d if x.startswith("-") and not x.startswith("---"))
        if adds or dels:
            lines.append(f"  Trang {i+1}: +{adds} dòng text, -{dels} dòng text")
    return lines


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Compare markups between two PDFs.")
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--csv")
    args = ap.parse_args(argv)

    for p in (args.old, args.new):
        if not Path(p).is_file():
            print(f"ERROR: không tìm thấy file: {p}", file=sys.stderr)
            return 2

    old_r, new_r = PdfReader(args.old), PdfReader(args.new)
    changes = diff_annots(extract_annots(old_r), extract_annots(new_r))

    counts = {"added": 0, "removed": 0, "moved": 0}
    for c in changes:
        counts[c["change"]] += 1

    print(f"So sánh markup / Markup compare: {Path(args.old).name} → {Path(args.new).name}")
    print(f"  Thêm/added:   {counts['added']}")
    print(f"  Xoá/removed:  {counts['removed']}")
    print(f"  Dời/moved:    {counts['moved']}")
    print("\nKhác biệt text theo trang / per-page text diff:")
    td = text_diff_summary(old_r, new_r)
    print("\n".join(td) if td else "  (không có thay đổi text đáng kể)")

    if changes:
        print("\nChi tiết markup / markup detail:")
        for c in sorted(changes, key=lambda x: (x["page"], x["change"])):
            extra = f"  {c.get('from','')}→{c.get('to','')}" if c["change"] == "moved" else ""
            content = (c["content"][:50] + "…") if len(c["content"]) > 50 else c["content"]
            print(f"  [{c['change']:7}] p{c['page']} {c['subtype']:9} {content!r}{extra}")

    if args.csv:
        out = Path(args.csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["change", "page", "subtype", "content", "x", "y"])
            for c in changes:
                w.writerow([c["change"], c["page"], c["subtype"], c["content"], c["x"], c["y"]])
        print(f"\nĐã ghi: {args.csv} ({len(changes)} thay đổi)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
