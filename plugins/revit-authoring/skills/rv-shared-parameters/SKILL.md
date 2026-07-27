---
name: rv-shared-parameters
description: Audit and standardize Revit shared parameters and family/project parameters. Analyzes a Revit shared parameter file (the tab-delimited .txt exported from Manage > Shared Parameters) to find duplicate GUIDs, duplicate names, missing descriptions, and group/data-type breakdowns; also gives guidance on type-vs-instance and naming standards. Use when cleaning up parameters, enforcing a company standard, or debugging shared-parameter issues. Triggers on "shared parameters", "family parameters", "parameter standard", "shared parameter file", "duplicate GUID", "chuẩn hoá parameter", "quản lý parameter Revit".
metadata:
  software: revit
  discipline: multi
  category: standards
---

# Family & Parameter Management — Quản lý parameter Revit

Rà soát & chuẩn hoá parameter của Revit. Phân tích **shared parameter file**
(file .txt tab-delimited xuất từ *Manage > Shared Parameters*) để tìm GUID
trùng, tên trùng, thiếu mô tả, và thống kê theo group/data type.
Audit & standardize Revit shared/family parameters.

## Khi nào dùng / When to use
- Dọn dẹp / chuẩn hoá bộ shared parameter của công ty.
- Gỡ lỗi shared parameter (GUID trùng làm param "biến mất" hoặc lệch giá trị).
- Cần thống kê parameter theo nhóm và kiểu dữ liệu.

## Cách dùng / How to use
1. Trong Revit: **Manage > Shared Parameters > Browse/Export** để có file `.txt`.
2. Chạy:
   ```bash
   python scripts/analyze_shared_params.py <shared_params.txt>
   python scripts/analyze_shared_params.py <shared_params.txt> --csv out/params.csv
   ```
   Thử nhanh với mẫu / quick test:
   ```bash
   python scripts/analyze_shared_params.py assets/sample_shared_params.txt
   ```

## Nó kiểm gì / what it checks
- **Duplicate GUID** — cùng GUID ở nhiều dòng param (lỗi nghiêm trọng).
- **Duplicate name** — cùng tên nhưng khác GUID (nhầm lẫn khi chọn param).
- **Missing description** — param không có mô tả (khó bảo trì).
- Thống kê theo **group** và **data type**.

## Type vs Instance (hướng dẫn nhanh)
- **Type**: giá trị chung cho mọi thể hiện cùng loại (vd Fire Rating của một wall type).
- **Instance**: mỗi thể hiện một giá trị (vd Mark, Comments, cao độ).
- Nguyên tắc: nếu giá trị thay đổi theo từng vật thể → instance; nếu là thuộc
  tính của "loại" → type.

## Đầu ra / Output
- Báo cáo tóm tắt + danh sách vấn đề (GUID/tên trùng, thiếu mô tả).
- (Tuỳ chọn) CSV toàn bộ param đã chuẩn hoá cột để đưa vào Excel.

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn. Xem `references/shared-parameter-format.md` để hiểu
  định dạng file. Việc *sửa* param trong model cần chạy trong Revit — dùng
  skill `rv-script-helper` để sinh script.
