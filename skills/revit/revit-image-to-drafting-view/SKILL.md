---
name: revit-image-to-drafting-view
description: Computes the placement size to bring a raster image (sketch, scan, reference photo) into a Revit drafting view for tracing — reads PNG/JPEG/GIF/BMP pixel dimensions and DPI with the standard library (no Pillow) and returns the Width/Height to set so the image represents a chosen real-world size, plus how big it prints on a sheet at a given scale; ships a pyRevit template that creates the drafting view and places the image. Use when converting an image or sketch into a drafting view, setting up an underlay to trace, or scaling a scanned drawing. Triggers on "image to drafting view", "convert image to draftingview", "place image in Revit", "trace image", "scale scanned drawing", "underlay", "convert ảnh thành drafting view", "chèn ảnh vào Revit".
license: MIT
metadata:
  software: revit
  discipline: multi
  category: automation
---

# Image to Drafting View — Chuyển ảnh thành drafting view (để trace)

Tính cỡ đặt để đưa ảnh raster (sketch, scan, ảnh tham chiếu) vào **drafting view**
Revit rồi trace: đọc kích thước px + DPI của PNG/JPEG/GIF/BMP bằng **thư viện
chuẩn** (không cần Pillow), trả về Width/Height cần đặt để ảnh rộng đúng cỡ thật,
và cỡ in trên sheet ở tỷ lệ cho trước. Kèm template pyRevit tạo drafting view &
đặt ảnh.
Computes drafting-view placement size for an image and ships a pyRevit template
to create the view and place it.

## Khi nào dùng / When to use
- Có sketch/scan/ảnh cần đưa vào Revit làm nền để trace bằng detail line.
- Cần scale ảnh đúng kích thước thật (biết một cạnh thật bao nhiêu mm).

## Cách dùng / How to use
```bash
# Đọc kích thước ảnh + tính cỡ đặt để ảnh rộng 10 m, in ở 1:100:
python scripts/image_scale.py <sketch.png> --real-width-mm 10000 --scale 100
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/image_scale.py assets/sample_sketch.png --real-width-mm 10000 --scale 100
```
Rồi trong Revit chạy `templates/pyrevit_place_image_drafting_view.py` (đặt
`IMAGE_PATH`, `WIDTH_FT` theo kết quả trên). Xem `references/`.

## Đầu ra / Output
- Kích thước ảnh (px), DPI (đọc từ file hoặc `--dpi`), cỡ native theo DPI (mm).
- Với `--real-width-mm`: **Width × Height** cần đặt trong drafting view (giữ tỷ lệ ảnh).
- Với `--scale`: cỡ in trên sheet ở tỷ lệ 1:S.

## Ghi chú / Notes
- Script chỉ dùng thư viện chuẩn (`struct`) — đọc header PNG/JPEG/GIF/BMP.
- Template chạy **trong Revit** (pyRevit, 2022+ cho API ImageInstance), dùng
  Transaction; không đọc secret / gọi mạng. Sau khi đặt: khoá ảnh, trace bằng
  detail line, rồi có thể xoá ảnh.
