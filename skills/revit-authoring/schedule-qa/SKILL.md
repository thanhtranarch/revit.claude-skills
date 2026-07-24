---
name: schedule-qa
description: QA Revit schedules and model data — find blank required parameters, mismatched values, and elements missing from schedules, and cross-check schedule exports against a standard. Use when validating model data completeness or preparing schedules for issue. Triggers on "schedule QA", "model data check", "missing parameters", "schedule export check", "kiểm tra schedule", "QA dữ liệu model".
status: scaffold
---

# Schedule QA — Kiểm tra schedule & dữ liệu model (SCAFFOLD)

> ⚠️ **Scaffold** — mới có khung. Expand before relying on it.

Kiểm tra chất lượng schedule/dữ liệu model Revit: parameter bắt buộc bị trống,
giá trị lệch chuẩn, phần tử thiếu trong schedule.

## Phạm vi dự kiến / planned scope
- Xuất schedule ra CSV rồi kiểm tra ô trống / giá trị ngoài danh mục cho phép.
- Đối chiếu với bộ quy tắc (required fields, allowed values).
- Báo cáo phần tử thiếu dữ liệu để sửa trước khi phát hành.

## Việc cần làm / TODO
- [ ] Script validate CSV schedule theo rule (tái dùng ý tưởng `validate_skill.py`).
- [ ] Định dạng rule (YAML: field → required/allowed).
- [ ] Reference cách export schedule ra CSV/TXT từ Revit.

Liên quan / related: `dynamo-pyrevit-helper`, `comment-aggregation`.
