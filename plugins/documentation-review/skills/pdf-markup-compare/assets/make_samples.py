#!/usr/bin/env python3
"""
make_samples.py — Sinh 2 PDF mẫu có annotation để thử compare_markup.py.
                  Generate two sample annotated PDFs to test compare_markup.py.
Chạy: python make_samples.py   → tạo rev_a.pdf, rev_b.pdf trong cùng thư mục.
"""
from pathlib import Path

from pypdf import PdfWriter
from pypdf.annotations import FreeText

HERE = Path(__file__).parent


def build(path: Path, notes):
    w = PdfWriter()
    w.add_blank_page(width=612, height=792)  # Letter
    for text, (x, y) in notes:
        ann = FreeText(
            text=text,
            rect=(x, y, x + 180, y + 24),
            font_size="10pt",
        )
        w.add_annotation(page_number=0, annotation=ann)
    with path.open("wb") as fh:
        w.write(fh)


# Rev A — bản gốc / original
build(HERE / "rev_a.pdf", [
    ("Note: verify beam depth", (72, 700)),
    ("RFI-012 pending", (72, 640)),
    ("Coordinate with MEP", (72, 580)),
])

# Rev B — thêm 1, xoá 1, dời 1 / add one, remove one, move one
build(HERE / "rev_b.pdf", [
    ("Note: verify beam depth", (300, 700)),   # moved
    ("Coordinate with MEP", (72, 580)),         # unchanged
    ("New: clearance check level 2", (72, 520)),  # added
    # "RFI-012 pending" removed
])

print("Đã tạo rev_a.pdf và rev_b.pdf")
