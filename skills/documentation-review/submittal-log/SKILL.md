---
name: submittal-log
description: Builds and tracks a submittal log from a submittal register — lifecycle status (pending/under review/approved/revise and resubmit/rejected), ball-in-court, overdue flags, spec-section grouping, and review-cycle stats. Use when managing construction submittals or producing a submittal status report. Triggers on "submittal log", "submittal register", "ball in court", "submittal status", "shop drawings", "nhật ký submittal", "theo dõi submittal".
license: MIT
---

# Submittal Log — Nhật ký & theo dõi submittal

Chuẩn hoá submittal register (CSV) thành log có trạng thái vòng đời, ball-in-court,
đánh dấu quá hạn, gom theo spec section, và thống kê **chu kỳ review** (ngày nhận
→ ngày trả).
Normalize a submittal register into a log with lifecycle status, ball-in-court,
overdue flags, spec grouping, and review-cycle stats.

## Khi nào dùng / When to use
- Có submittal register export (Procore/ACC/Excel) dạng CSV.
- Cần: trạng thái theo bên đang giữ (ball-in-court), danh sách quá hạn, số cần
  nộp lại (revise & resubmit), thời gian review trung bình.

## Cách dùng / How to use
```bash
python scripts/build_submittal_log.py <submittals.csv>
python scripts/build_submittal_log.py <submittals.csv> --as-of 2026-07-24 --csv out/submittal_log.csv
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/build_submittal_log.py assets/sample_submittals.csv --as-of 2026-07-24
```

## Đầu ra / Output
- Tổng / open / complete; đếm theo **status**, **ball-in-court**, **spec section**.
- Số **cần nộp lại** (revise & resubmit / rejected); danh sách **quá hạn**.
- Chu kỳ review (ngày nhận→trả): trung bình / trung vị / max.
- (Tuỳ chọn) CSV log + cột `overdue`, `cycle_days`.

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `datetime`, `statistics`).
- Hoàn tất / complete: status ∈ {approved, approved as noted, closed,
  no exceptions taken, for record}. Chỉ submittal chưa hoàn tất mới tính quá hạn.
- Tự dò cột theo alias; kết hợp `comment-aggregation` khi có nhiều nguồn markup.
