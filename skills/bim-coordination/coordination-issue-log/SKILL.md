---
name: coordination-issue-log
description: Turn clash results and coordination-meeting findings into a tracked issue log with owner, discipline, status, and target date — merging multiple meeting rounds by ID and exporting a CSV mapped to ACC/BIM360 Issues import. Use when running coordination meetings and needing to assign and track clash/coordination items over time. Triggers on "coordination log", "clash issue log", "assign clashes", "coordination meeting", "nhật ký coordination", "giao clash".
---

# Coordination Issue Log — Nhật ký issue coordination

Biến kết quả clash + phát hiện họp coordination thành nhật ký issue có người phụ
trách, bộ môn, trạng thái, target date. **Gộp nhiều vòng họp** theo id (vòng sau
đè vòng trước), đánh dấu quá hạn, và xuất CSV khớp cột import Issues của ACC/BIM360.
Merge multiple coordination rounds into a tracked issue log and export an
ACC/BIM360-ready CSV.

## Khi nào dùng / When to use
- Chạy họp coordination định kỳ, cần giao & theo dõi clash qua thời gian.
- Có nhiều bản export clash (mỗi vòng một CSV) cần gộp giữ trạng thái mới nhất.

## Cách dùng / How to use
```bash
# gộp nhiều vòng, giữ trạng thái mới nhất theo id:
python scripts/build_issue_log.py <round1.csv> <round2.csv> --as-of 2026-07-24
# xuất log đã gộp + CSV import ACC:
python scripts/build_issue_log.py <round1.csv> <round2.csv> \
       --csv out/issue_log.csv --acc-csv out/acc_import.csv
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/build_issue_log.py assets/sample_round1.csv assets/sample_round2.csv --as-of 2026-07-24
```

## Đầu ra / Output
- Tóm tắt gộp: số file, số issue riêng biệt, open vs closed.
- Đếm theo **status / discipline / owner**; danh sách **quá hạn** theo target date.
- (Tuỳ chọn) `--csv` log đã gộp (kèm `source`, `overdue`);
  `--acc-csv` khớp cột **Title, Description, Status, Assignee, Location, Due Date**.

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `datetime`).
- Gộp theo `id`; vòng sau đè vòng trước nhưng giữ `raised_date` sớm nhất.
- Đóng / closed: status ∈ {closed, resolved, approved, done, verified, complete}
  **hoặc** có ngày đóng.
- Cột ACC có thể cần chỉnh theo template dự án; tiền xử lý bằng `clash-report-analysis`.
