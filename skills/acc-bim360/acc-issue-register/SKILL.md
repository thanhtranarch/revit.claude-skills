---
name: acc-issue-register
description: Normalizes an Autodesk Construction Cloud (ACC) or BIM360 issues CSV export into a clean register and summary — counts by status, assignee, discipline, and overdue flags against due dates. Use when the user has an ACC/BIM360 issues export and wants a tidy register, a status breakdown, an overdue list, or a weekly coordination summary. Triggers on "ACC issues", "BIM360 issues", "issue register", "overdue issues", "tổng hợp issue", "báo cáo issue ACC".
license: MIT
metadata:
  software: acc-bim360
  discipline: multi
  category: coordination
---

# ACC / BIM360 Issue Register — Chuẩn hoá & tóm tắt issue

Chuẩn hoá file CSV export issue từ **ACC/BIM360** thành register gọn gàng và
bảng tóm tắt: đếm theo trạng thái, người phụ trách, bộ môn; đánh dấu quá hạn.
Normalize an ACC/BIM360 issues CSV into a clean register + summary with overdue
flags.

## Khi nào dùng / When to use
- Có file CSV export từ ACC (Issues → Export) hoặc BIM360.
- Cần: thống kê theo status/assignee/discipline, danh sách quá hạn, tóm tắt tuần.

## Cách làm / How to use
```bash
python scripts/normalize_issues.py <acc_export.csv>
# xuất register CSV đã chuẩn hoá + cột overdue:
python scripts/normalize_issues.py <acc_export.csv> --csv out/issue_register.csv
# đổi mốc so hạn (mặc định = hôm nay):
python scripts/normalize_issues.py <acc_export.csv> --as-of 2026-07-24
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/normalize_issues.py assets/sample_issues.csv --as-of 2026-07-24
```

## Đầu ra / Output
- Tóm tắt: tổng số, đếm theo **status / assignee / discipline**, số **quá hạn**.
- (Tuỳ chọn) CSV register chuẩn hoá cột + cột `overdue` (yes/no).

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `datetime`).
- Tự dò cột (alias không phân biệt hoa/thường): `id/title/status/assignee/
  discipline/due date/location`. Cột thiếu để trống.
- Issue đã `Closed`/`Resolved` không tính là quá hạn.
