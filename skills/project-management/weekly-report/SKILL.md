---
name: weekly-report
description: Assembles a weekly BIM/coordination status report from multiple register CSVs (issue logs, RFI trackers, clash registers, change orders) — open vs closed counts, overdue items, and week-over-week deltas from a saved snapshot. Use when preparing a recurring weekly coordination or project status report. Triggers on "weekly report", "status report", "week over week", "coordination summary", "báo cáo tuần", "tổng hợp trạng thái tuần".
license: MIT
---

# Weekly Report — Báo cáo trạng thái tuần

Tổng hợp báo cáo trạng thái tuần từ **nhiều register CSV** (issue log, RFI, clash,
change order): open vs closed, quá hạn, và **biến động tuần** (week-over-week) từ
snapshot đã lưu. Xuất Markdown gọn cho họp tuần.
Assemble a weekly status report from multiple register CSVs with open/closed
counts, overdue items, and week-over-week deltas. Outputs Markdown.

## Khi nào dùng / When to use
- Chuẩn bị báo cáo tuần định kỳ từ nhiều nguồn (issue/RFI/clash/change order).
- Cần tổng hợp một bảng + danh sách quá hạn + so với tuần trước.

## Cách dùng / How to use
```bash
# nhiều nguồn, mỗi nguồn một nhãn:
python scripts/weekly_report.py \
  --source Issues=<issues.csv> --source RFIs=<rfis.csv> --as-of 2026-07-24

# lưu snapshot tuần này + so với tuần trước + ghi file:
python scripts/weekly_report.py --source Issues=<issues.csv> \
  --prev last_week.json --snapshot this_week.json --out out/weekly.md
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/weekly_report.py \
  --source Issues=assets/sample_issues.csv \
  --source RFIs=assets/sample_rfis.csv \
  --prev assets/sample_prev_snapshot.json --as-of 2026-07-24
```

## Đầu ra / Output
- Bảng Markdown: mỗi nguồn → total / open / closed / overdue / **Δ open** so tuần trước.
- Danh sách **quá hạn** cho từng nguồn.
- (Tuỳ chọn) `--snapshot` ghi JSON tuần này (dùng làm `--prev` tuần sau);
  `--out` ghi Markdown ra file.

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `json`, `datetime`).
- Tự dò cột **status** & **due** theo alias phổ biến; đóng = status thuộc tập
  {closed, resolved, answered, approved, done, complete, void, rejected…}.
- Nguồn khai báo dạng `Nhãn=đường_dẫn.csv`, lặp `--source` nhiều lần.
- Kết hợp tốt với `acc-issue-register`, `rfi-tracker`, `clash-report-analysis`,
  `change-order-log` (chạy chúng trước rồi đưa CSV vào đây).
