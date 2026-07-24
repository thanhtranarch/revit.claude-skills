#!/usr/bin/env python3
"""
parse_warnings.py — Tổng hợp & ưu tiên warning từ HTML export của Revit.
                    Triage a Revit "Review Warnings" HTML export.

Chỉ dùng thư viện chuẩn (html.parser). / Stdlib only.

Usage:
    python parse_warnings.py warnings.html
    python parse_warnings.py warnings.html --csv warnings.csv
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

# Từ khoá -> mức nghiêm trọng (khớp không phân biệt hoa/thường).
HIGH_KEYWORDS = [
    "duplicate", "identical instances", "overlap", "coincident", "same location",
    "not enclosed", "room is not", "area is not", "join", "instances of a group",
]
MEDIUM_KEYWORDS = [
    "mismatch", "off axis", "slightly", "type mark", "mark value",
    "no phase", "unconnected", "out of date",
]

ID_RE = re.compile(r"\bid\s+\d+", re.I)


class WarningTableParser(HTMLParser):
    """Trích text từng ô <td>/<li> theo dòng. / extract cell text per row."""

    def __init__(self):
        super().__init__()
        self.rows: list[list[str]] = []
        self._cur: list[str] = []
        self._buf: list[str] = []
        self._in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag in ("td", "th", "li"):
            self._in_cell = True
            self._buf = []
        elif tag in ("tr",):
            self._cur = []

    def handle_endtag(self, tag):
        if tag in ("td", "th", "li"):
            self._in_cell = False
            self._cur.append("".join(self._buf).strip())
        elif tag in ("tr", "ul", "ol"):
            if self._cur:
                self.rows.append(self._cur)
                self._cur = []

    def handle_data(self, data):
        if self._in_cell:
            self._buf.append(data)


def severity(message: str) -> str:
    m = message.lower()
    if any(k in m for k in HIGH_KEYWORDS):
        return "HIGH"
    if any(k in m for k in MEDIUM_KEYWORDS):
        return "MEDIUM"
    return "LOW"


def extract_warnings(html: str) -> list[str]:
    """Trả về danh sách message (mỗi lần xuất hiện 1 phần tử)."""
    p = WarningTableParser()
    p.feed(html)
    messages: list[str] = []
    for row in p.rows:
        cells = [c for c in row if c]
        if not cells:
            continue
        first = cells[0]
        # dòng chỉ chứa element id (chi tiết của warning) -> bỏ qua, không đếm
        if ID_RE.search(first) and not re.sub(ID_RE, "", first).strip():
            continue
        # dòng message: bỏ tiền tố "Warning n:" nếu có
        msg = re.sub(r"^\s*warning\s*\d*\s*:?\s*", "", first, flags=re.I).strip()
        if msg and not ID_RE.fullmatch(msg):
            messages.append(msg)
    return messages


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Triage Revit warnings HTML export.")
    ap.add_argument("html")
    ap.add_argument("--csv")
    args = ap.parse_args(argv)

    path = Path(args.html)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.html}", file=sys.stderr)
        return 2

    messages = extract_warnings(path.read_text(encoding="utf-8", errors="replace"))
    if not messages:
        print("Không trích được warning nào — kiểm tra file có phải HTML export "
              "của Review Warnings không.", file=sys.stderr)
        return 2

    by_msg = Counter(messages)
    by_sev = Counter(severity(m) for m in messages)

    print(f"Tổng warning / total: {len(messages)}  |  số nhóm message: {len(by_msg)}")
    print("\nTheo mức nghiêm trọng / by severity:")
    for sev in ("HIGH", "MEDIUM", "LOW"):
        if by_sev.get(sev):
            print(f"  {sev:6} {by_sev[sev]:5}")

    print("\nTop message hay gặp / most frequent:")
    for msg, n in by_msg.most_common(10):
        print(f"  {n:4}  [{severity(msg):6}] {msg[:70]}")

    if args.csv:
        out = Path(args.csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["count", "severity", "message"])
            for msg, n in by_msg.most_common():
                w.writerow([n, severity(msg), msg])
        print(f"\nĐã ghi: {args.csv} ({len(by_msg)} nhóm)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
