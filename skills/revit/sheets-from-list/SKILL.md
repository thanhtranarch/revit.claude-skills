---
name: sheets-from-list
description: Validates a sheet list from a CSV and generates a pyRevit script to batch-create Revit sheets — checks sheet numbers against a pattern, flags duplicates and missing names, groups counts by discipline, and emits a plan JSON that the bundled pyRevit template turns into ViewSheets (skipping numbers that already exist). Use when setting up many sheets at once from a drawing register or sheet schedule instead of creating them one by one. Triggers on "create sheets", "batch sheets", "sheets from list", "sheet register to Revit", "set up sheets", "tạo sheet hàng loạt", "dựng sheet từ danh sách".
license: MIT
metadata:
  software: revit
  discipline: multi
  category: automation
---

# Sheets from List — Tạo sheet hàng loạt từ danh sách

Kiểm danh sách sheet (CSV) và sinh script pyRevit tạo sheet hàng loạt: kiểm số
sheet theo pattern, bắt **trùng số** & **thiếu tên**, đếm theo bộ môn, và xuất
**plan JSON** để template pyRevit tạo `ViewSheet` (bỏ qua số đã tồn tại).
Validates a sheet list and generates a pyRevit script to batch-create sheets.

## Khi nào dùng / When to use
- Cần dựng nhiều sheet một lúc từ drawing register / sheet schedule.
- Muốn soát danh sách (trùng số, thiếu tên) trước khi tạo.

## Cách dùng / How to use
```bash
# 1) Kiểm & xem kế hoạch theo bộ môn:
python scripts/plan_sheets.py <sheets.csv>
# 2) Xuất plan JSON cho template pyRevit:
python scripts/plan_sheets.py <sheets.csv> --json > sheets.json
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/plan_sheets.py assets/sample_sheet_list.csv
```
Rồi trong Revit chạy `templates/pyrevit_create_sheets.py` (đặt `PLAN=sheets.json`).

## Đầu ra / Output
- Đếm sheet theo **bộ môn**; danh sách **lỗi** (trùng số / sai pattern / thiếu tên).
- Số sheet **sẵn sàng tạo**; `--json` → plan gồm `number`, `name`, `titleblock`.
- Exit 1 nếu có lỗi cần sửa (tiện gate trước khi tạo).

## Ghi chú / Notes
- Script chỉ dùng thư viện chuẩn (`csv`, `json`, `re`).
- Tự dò cột Sheet Number / Sheet Name / Titleblock / Discipline theo alias.
- Template chạy **trong Revit** (pyRevit), dùng Transaction, **bỏ qua sheet trùng
  số** đã có; chọn đúng titleblock theo dự án trước khi chạy. Bổ trợ
  `sheet-naming-check` (chuẩn số/tên) trước khi tạo.
