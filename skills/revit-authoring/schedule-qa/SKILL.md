---
name: schedule-qa
description: Validates the data behind Revit schedules by checking a schedule exported to CSV/TSV against a rules file — required fields that must not be blank, allowed-value lists, and columns that must be unique (e.g. Mark). Reports each violation with its row so the model can be fixed before issue. Use when validating model-data completeness, checking a schedule export against a company standard, or finding blank/duplicate Marks. Triggers on "schedule QA", "model data check", "missing parameters", "duplicate mark", "validate schedule", "kiểm tra schedule", "QA dữ liệu model".
license: MIT
---

# Schedule QA — Kiểm tra schedule & dữ liệu model

Kiểm tra dữ liệu đứng sau schedule Revit: export schedule ra CSV/TSV rồi validate
theo một **rules file** (YAML) — cột bắt buộc không được trống, danh sách giá
trị cho phép, cột phải duy nhất. Báo lỗi kèm số dòng.
Validate a Revit schedule CSV against a rules file.

## Khi nào dùng / When to use
- Kiểm tra tính đầy đủ của dữ liệu model trước khi phát hành.
- Bắt Mark trống/trùng, giá trị ngoài danh mục cho phép, thiếu trường bắt buộc.

## Cách dùng / How to use
1. Trong Revit: mở schedule → **Export > Schedule** (ra `.txt`/CSV tab/comma).
2. Viết rules (xem `assets/sample_rules.yaml`) rồi chạy:
   ```bash
   python scripts/check_schedule.py <schedule.csv> --rules <rules.yaml>
   ```
   Thử nhanh với mẫu / quick test:
   ```bash
   python scripts/check_schedule.py assets/sample_schedule.csv --rules assets/sample_rules.yaml
   ```

## Rules file (YAML)
```yaml
delimiter: ","            # hoặc "\t" nếu export tab-delimited
required: [Mark, Fire Rating]        # các cột không được để trống
unique:   [Mark]                     # các cột phải duy nhất
allowed:                             # danh sách giá trị hợp lệ theo cột
  Fire Rating: ["1 HR", "2 HR", "None"]
```
Xem thêm `references/rules-reference.md`.

## Đầu ra / Output
- Danh sách vi phạm: loại lỗi · cột · **dòng** · giá trị.
- Exit code ≠ 0 nếu có vi phạm (tiện dùng trong quy trình QA/CI).

## Ghi chú / Notes
- Cần `pyyaml` (đã có trong `requirements.txt`). CSV đọc bằng thư viện chuẩn.
- Chỉ kiểm dữ liệu đã export; để *sửa* trong model, dùng `dynamo-pyrevit-helper`.
