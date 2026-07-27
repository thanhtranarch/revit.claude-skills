---
name: revit-batch-export
description: Generates and adapts pyRevit/Dynamo scripts to batch-export Revit sheets and views to PDF, DWG, DWF, NWC, or IFC with a consistent file-naming convention (e.g. SheetNumber-SheetName-Rev). Use when the user needs to export many sheets at once, standardize export file names, or automate a recurring issue/export. Triggers on "batch export", "export sheets", "export PDF Revit", "export DWG", "naming convention export", "xuất bản vẽ hàng loạt", "export NWC/IFC".
license: MIT
metadata:
  software: revit
  discipline: multi
  category: automation
---

# Revit Batch Export — Xuất bản vẽ hàng loạt

Sinh & tuỳ biến script pyRevit/Dynamo để export hàng loạt sheet/view ra
**PDF/DWG/DWF/NWC/IFC** với quy ước đặt tên file thống nhất
(vd `SheetNumber-SheetName-Rev`).
Generate scripts to batch-export Revit sheets/views with consistent naming.

## Khi nào dùng / When to use
- Cần export nhiều sheet cùng lúc, hoặc chuẩn hoá tên file export.
- Tự động hoá quy trình phát hành/issue định kỳ.

## Cách dùng / How to use
1. Xác định: định dạng (PDF/DWG/NWC/IFC), phạm vi (sheet set / theo revision),
   quy ước tên file.
2. Lấy mẫu trong `templates/` và tuỳ biến; xem lưu ý trong `references/`.
3. Chạy trong Revit qua pyRevit (button/script) hoặc Dynamo.

## Quy ước tên file / naming convention
Mẫu mặc định: `{SheetNumber}-{SheetName}-{Revision}` (bỏ ký tự không hợp lệ
`\ / : * ? " < > |`). Điều chỉnh trong biến `NAME_TEMPLATE` của script.

## An toàn / safety
- Script export **chỉ đọc** model + ghi file ra thư mục đích; không sửa model
  → không cần Transaction.
- Kiểm tra thư mục đích tồn tại & đủ dung lượng trước khi chạy loạt lớn.
- Với PDF: Revit 2022+ có API export PDF gốc (`PDFExportOptions`); bản cũ hơn
  cần in qua máy in PDF — xem references.

## Tài nguyên / Resources
- `templates/pyrevit_batch_export_sheets.py` — mẫu export sheet ra PDF theo tên chuẩn.
- `references/export-notes.md` — khác biệt định dạng & phiên bản, mẹo đặt tên.

## Ghi chú / Notes
- Đây là skill sinh-script (chạy trong Revit), không phải CLI của repo. Kết hợp
  `revit-dynamo-pyrevit-helper` cho các tuỳ biến sâu hơn.
