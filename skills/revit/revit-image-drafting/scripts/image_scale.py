#!/usr/bin/env python3
"""
image_scale.py — Đọc kích thước ảnh (px, DPI) & tính cỡ đặt trong drafting view.
                 Read image size (px, DPI) & compute placement size for a Revit
                 drafting view (for tracing / underlay).

Đọc header PNG/JPEG/GIF/BMP bằng thư viện chuẩn (không cần Pillow). Tính:
- cỡ "native" theo DPI, cỡ đặt (Width×Height) để ảnh rộng đúng X mm, và cỡ in
  trên sheet ở tỷ lệ 1:S. Chỉ dùng thư viện chuẩn.

Usage:
    python image_scale.py sketch.png
    python image_scale.py sketch.png --real-width-mm 10000 --scale 100
Exit: 0 = ok, 2 = usage / không đọc được ảnh.
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

MM_PER_INCH = 25.4


def _png_dpi(path: Path):
    data = path.read_bytes()
    idx = data.find(b"pHYs")
    if idx == -1 or idx + 13 > len(data):
        return None
    ppu_x, _ppu_y, unit = struct.unpack(">IIB", data[idx + 4:idx + 13])
    if unit == 1 and ppu_x:                      # unit 1 = mét / metre
        return round(ppu_x * 0.0254)
    return None


def _jpeg_size(path: Path):
    with path.open("rb") as f:
        f.read(2)                                # SOI
        while True:
            b = f.read(1)
            if not b:
                return None
            if b != b"\xff":
                continue
            marker = f.read(1)
            while marker == b"\xff":
                marker = f.read(1)
            m = marker[0]
            if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                f.read(3)                        # length(2) + precision(1)
                h, w = struct.unpack(">HH", f.read(4))
                return w, h, None, "JPEG"
            seg = f.read(2)
            if len(seg) < 2:
                return None
            f.seek(struct.unpack(">H", seg)[0] - 2, 1)


def get_image_size(path: Path):
    head = path.read_bytes()[:64]
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", head[16:24])
        return w, h, _png_dpi(path), "PNG"
    if head[:2] == b"\xff\xd8":
        return _jpeg_size(path)
    if head[:6] in (b"GIF87a", b"GIF89a"):
        w, h = struct.unpack("<HH", head[6:10])
        return w, h, None, "GIF"
    if head[:2] == b"BM" and len(head) >= 42:
        w, h = struct.unpack("<ii", head[18:26])
        ppm = struct.unpack("<i", head[38:42])[0]
        return w, abs(h), (round(ppm * 0.0254) if ppm else None), "BMP"
    return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Compute Revit drafting-view placement size for an image.")
    ap.add_argument("image", help="Ảnh PNG/JPEG/GIF/BMP")
    ap.add_argument("--dpi", type=float, help="Ghi đè DPI (mặc định lấy từ ảnh hoặc 96)")
    ap.add_argument("--real-width-mm", type=float,
                    help="Muốn ảnh rộng đúng bao nhiêu mm trong model (đặt Width theo cỡ thật)")
    ap.add_argument("--scale", type=float, help="Mẫu số tỷ lệ view/sheet (vd 100 = 1:100)")
    args = ap.parse_args(argv)

    path = Path(args.image)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.image}", file=sys.stderr)
        return 2
    info = get_image_size(path)
    if not info:
        print("ERROR: không đọc được kích thước ảnh (hỗ trợ PNG/JPEG/GIF/BMP).", file=sys.stderr)
        return 2

    px_w, px_h, src_dpi, fmt = info
    dpi = args.dpi or src_dpi or 96
    aspect = px_h / px_w if px_w else 0
    native_w = px_w / dpi * MM_PER_INCH
    native_h = px_h / dpi * MM_PER_INCH

    print(f"Ảnh / Image: {path.name}  [{fmt}]")
    print(f"  Kích thước / size: {px_w} × {px_h} px")
    print(f"  DPI: {dpi:g}"
          f"{'' if src_dpi else '  (không có trong file — mặc định/override)'}")
    print(f"  Cỡ native @DPI / native size: {native_w:,.1f} × {native_h:,.1f} mm")

    if args.real_width_mm:
        placed_w = args.real_width_mm
        placed_h = placed_w * aspect
        print(f"\nĐặt trong drafting view / place with:")
        print(f"  Width  = {placed_w:,.1f} mm   (đặt cỡ thật ảnh đại diện)")
        print(f"  Height = {placed_h:,.1f} mm   (tự theo tỷ lệ ảnh {px_w}:{px_h})")
        if args.scale:
            print(f"  In trên sheet @1:{args.scale:g} / on sheet: "
                  f"{placed_w / args.scale:,.1f} × {placed_h / args.scale:,.1f} mm")
    else:
        print("\n→ Dùng --real-width-mm để tính Width đặt theo cỡ thật (tracing/underlay).")
        if args.scale:
            print(f"  In native trên sheet @1:{args.scale:g} / native on sheet: "
                  f"{native_w / args.scale:,.1f} × {native_h / args.scale:,.1f} mm")

    print("\nMẹo / tip: tạo Drafting View → Insert > Image → đặt Width như trên → "
          "khoá ảnh → trace bằng detail line. Xem references/.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
