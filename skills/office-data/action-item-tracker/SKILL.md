---
name: action-item-tracker
description: Tracks meeting and coordination action items from a register — owner, status, due date, aging buckets, overdue flags, and rollups by owner, meeting, and priority. Use when managing open actions from coordination or project meetings and needing an open-action list, an owner workload view, or an overdue report. Triggers on "action items", "action tracker", "open actions", "meeting actions", "who owns", "theo dõi action", "việc cần làm sau họp".
license: MIT
metadata:
  software: office-data
  discipline: multi
  category: project-management
---

# Action Item Tracker — Theo dõi action item sau họp

Theo dõi action item (họp coordination/dự án) từ register CSV: owner, trạng
thái, hạn, nhóm **aging**, cờ quá hạn; gom theo **owner / cuộc họp / ưu tiên**.
Track meeting & coordination action items: owner, status, due, aging buckets,
overdue flags, and rollups by owner, meeting, and priority.

## Khi nào dùng / When to use
- Có danh sách action item (CSV) từ biên bản họp / coordination.
- Cần: danh sách action đang mở, tải công việc theo owner, action quá hạn,
  nhóm theo cuộc họp hoặc mức ưu tiên.

## Cách dùng / How to use
```bash
python scripts/track_actions.py <actions.csv>
python scripts/track_actions.py <actions.csv> --as-of 2026-07-24
# lọc theo owner + xuất CSV:
python scripts/track_actions.py <actions.csv> --owner "J. Tran" --csv out/actions.csv
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/track_actions.py assets/sample_actions.csv --as-of 2026-07-24
```

## Đầu ra / Output
- Tổng / open / closed.
- Rollup theo **owner**, **cuộc họp**, **ưu tiên** (chỉ item đang mở).
- **Aging** theo số ngày mở; danh sách **quá hạn**.
- (Tuỳ chọn) CSV register + cột `days_open`, `overdue`, `bucket`.

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `datetime`).
- Đóng / closed: status ∈ {closed, done, complete(d), resolved, cancelled} **hoặc**
  có ngày đóng. Chỉ item đang mở mới tính quá hạn/aging.
- `--owner` lọc gần đúng (chứa chuỗi, không phân biệt hoa/thường).
