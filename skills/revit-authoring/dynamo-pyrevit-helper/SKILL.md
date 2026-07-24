---
name: dynamo-pyrevit-helper
description: Help write, review, and troubleshoot Revit automation scripts using pyRevit (IronPython/CPython) or Dynamo Python nodes — common tasks like setting parameters in bulk, renaming views/sheets, exporting, and collecting elements by category. Use when the user is scripting Revit, mentions pyRevit, Dynamo, RevitAPI, FilteredElementCollector, Transaction, or wants to automate a repetitive Revit task. Triggers on "pyRevit", "Dynamo script", "Revit API", "automate Revit", "script Revit", "set parameter Revit", "viết script Revit".
---

# Dynamo / pyRevit Helper — Trợ giúp script Revit

Hỗ trợ viết / rà soát / gỡ lỗi script tự động hoá Revit bằng **pyRevit** hoặc
**Dynamo Python node** cho các tác vụ lặp: đặt tham số hàng loạt, đổi tên
view/sheet, export, thu thập phần tử theo category.
Help author & review Revit automation scripts (pyRevit / Dynamo Python).

## Khi nào dùng / When to use
- Người dùng cần script Revit cho tác vụ lặp lại, hoặc đang gặp lỗi RevitAPI
  (Transaction, FilteredElementCollector, đơn vị, null parameter…).

## Quy tắc an toàn khi sinh script / Safety rules
1. **Mọi thay đổi model phải nằm trong `Transaction`** (pyRevit) — bắt đầu/commit
   rõ ràng; Dynamo tự quản transaction nên KHÔNG tự mở transaction trong node.
2. Luôn kiểm tra `param is not None` và `not param.IsReadOnly` trước khi `.Set()`.
3. Đơn vị nội bộ Revit = feet/API units — quy đổi bằng `UnitUtils`, đừng hard-code.
4. Không xoá phần tử trừ khi được yêu cầu rõ; ưu tiên thao tác đọc trước khi ghi.
5. Ghi rõ script chạy trên **pyRevit** hay **Dynamo**, và bản Revit mục tiêu.

## Cách dùng / How to use
1. Xác định môi trường: pyRevit (button/script) hay Dynamo (Python node).
2. Tham khảo mẫu trong `templates/` và ghi chú API trong `references/`.
3. Sinh script tối thiểu, có comment, có xử lý null + transaction đúng chuẩn.

## Tài nguyên / Resources
- `templates/pyrevit_set_parameter.py` — mẫu đặt param hàng loạt (có Transaction).
- `templates/dynamo_collect_by_category.py` — mẫu thu thập phần tử trong Dynamo.
- `references/revit-api-cheatsheet.md` — pattern hay dùng + bẫy thường gặp.

## Ghi chú / Notes
- Các script này **chạy trong Revit** (pyRevit/Dynamo), không chạy bằng Python
  ngoài — chúng là mẫu/tham chiếu, không phải CLI của repo.
- Kiểm tra tương thích IronPython 2.7 vs CPython3 tuỳ phiên bản pyRevit/Dynamo.
