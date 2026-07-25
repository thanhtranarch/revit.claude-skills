---
name: comment-aggregation
description: Aggregates review comments / RFIs / markups from multiple CSV exports (Bluebeam markup summary, ACC/BIM360 issues, reviewer spreadsheets) into one consolidated, de-duplicated Excel register with status and discipline breakdowns. Use when the user has comments scattered across several files and wants a single tracked register, a comment log, or an RFI summary. Triggers on "aggregate comments", "tổng hợp comment", "consolidate RFI", "comment register", "gộp markup", "tổng hợp ý kiến review".
license: MIT
metadata:
  software: bluebeam-pdf
  discipline: multi
  category: documentation
---

# Comment Aggregation — Tổng hợp comment / RFI

Gộp comment/RFI/markup từ nhiều file CSV (Bluebeam markup summary, ACC/BIM360
issues, bảng review) thành **một register Excel** thống nhất, khử trùng lặp,
kèm thống kê theo trạng thái & bộ môn.
Consolidate review comments from multiple CSV exports into one de-duplicated
Excel register with status/discipline breakdowns.

## Khi nào dùng / When to use
- Comment nằm rải rác ở nhiều nguồn (mỗi reviewer/mỗi phần mềm một file).
- Cần một bảng theo dõi duy nhất để giao việc và đóng comment.

## Đầu vào / Input
Một hoặc nhiều CSV. Script tự dò các cột phổ biến (không phân biệt hoa/thường,
chấp nhận tên thay thế):
- `id`, `subject`/`title`, `comment`/`description`/`contents`, `author`/`created by`,
  `discipline`/`trade`, `status`, `location`/`sheet`/`page`, `date`.
Cột thiếu sẽ để trống; cột lạ được bỏ qua. Xem `references/column-aliases.md`.

## Cách làm / How to use
```bash
python scripts/aggregate_comments.py in1.csv in2.csv -o out/comment_register.xlsx
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/aggregate_comments.py assets/bluebeam.csv assets/acc_issues.csv -o /tmp/register.xlsx
```

## Đầu ra / Output
File `.xlsx` gồm:
- Sheet **Register**: toàn bộ comment đã chuẩn hoá cột + cột `source` (file gốc).
- Sheet **Summary**: đếm theo `status` và theo `discipline`.
Trùng lặp (cùng subject + comment + location) được gộp, ghi rõ số nguồn.

## Ghi chú / Notes
- Cần `openpyxl` (xem `requirements.txt`). CSV đọc bằng thư viện chuẩn.
- Muốn thêm alias cột, sửa `COLUMN_ALIASES` trong script hoặc xem references.
