---
name: revit-create-family
description: Turns a table of family types and parameter values into a Revit type catalog (.txt) and a pyRevit script that batch-creates the types in an open family. Reads a CSV where each row is a family type and each column is a parameter (headers may carry a Name##TYPE##unit spec), validates it (duplicate type/parameter names, blank type names, non-numeric values in dimensional columns, commas that would break the catalog), then emits a correctly formatted Revit type catalog or a plan JSON for the bundled pyRevit template. Use when setting up many sizes/types of a family at once — doors, windows, furniture, equipment — from a schedule instead of adding each type by hand. Triggers on "create family types", "type catalog", "family from schedule", "batch family types", "size table to Revit", "tạo type family hàng loạt", "type catalog Revit", "dựng family từ bảng".
license: MIT
metadata:
  software: revit
  discipline: multi
  category: automation
---

# Revit Create Family (Types) — Tạo type family hàng loạt từ bảng

Biến **bảng type + tham số** (CSV) thành **Revit type catalog** (`.txt`) đúng định
dạng và một script **pyRevit** tạo type hàng loạt trong family đang mở. Mỗi dòng
CSV = một family type; mỗi cột = một tham số. Kiểm hợp lệ trước khi phát cho team.
Turns a family-types table into a Revit type catalog and a pyRevit batch-create script.

## Khi nào dùng / When to use
- Cần dựng **nhiều size/type** của một family (cửa, cửa sổ, nội thất, thiết bị)
  từ một bảng schedule thay vì thêm tay từng type.
- Muốn xuất **type catalog** (`Door.txt` cạnh `Door.rfa`) để chọn type khi load.
- Muốn soát bảng (trùng type, sai kiểu số, dấu phẩy phá catalog) trước khi tạo.

## Cách dùng / How to use
CSV: cột đầu (hoặc cột tên `Type`) = tên type; các cột còn lại = tham số. Header
cột có thể ghi kiểu/đơn vị: `Width##LENGTH##millimeters`; không ghi → mặc định
text (`##OTHER##`).
```bash
# 1) Kiểm + xem trước type catalog:
python scripts/build_type_catalog.py <types.csv>
# 2) Ghi type catalog .txt (đặt cạnh .rfa, cùng tên family):
python scripts/build_type_catalog.py <types.csv> --catalog Door.txt
# 3) Xuất plan JSON cho template pyRevit:
python scripts/build_type_catalog.py <types.csv> --json > plan.json
```
Thử nhanh với mẫu / quick test:
```bash
python scripts/build_type_catalog.py assets/sample_family_types.csv
```
Rồi trong **Family Editor** chạy `templates/pyrevit_create_family_types.py`
(đặt `PLAN=plan.json`).

## Đầu ra / Output
- Type catalog `.txt` đúng định dạng Revit (ô header đầu để trống; cột
  `Name##TYPE##unit`), hoặc plan JSON gồm `parameters` + `types`.
- Danh sách **lỗi**: trùng tên type / tên cột, thiếu tên type, giá trị **không
  phải số** ở cột dimensional, **dấu phẩy trong giá trị**. Exit 1 nếu có lỗi.

## Ghi chú / Notes
- Script chỉ dùng thư viện chuẩn (`csv`, `json`). Chi tiết định dạng catalog:
  [`references/type-catalog-format.md`](references/type-catalog-format.md).
- Template chạy **trong Family Editor** (pyRevit), dùng Transaction, **bỏ qua
  type trùng tên**, và chỉ set tham số đã tồn tại trong family.
- Giá trị dimensional theo **đơn vị khai ở header** — Revit tự quy đổi khi nạp.
- Bổ trợ `revit-shared-parameters` (chuẩn hoá tham số) và `revit-schedule-qa`
  (QA dữ liệu type sau khi tạo).
