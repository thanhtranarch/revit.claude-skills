---
name: weekly-report
description: Assemble a weekly BIM/coordination status report from clash registers, issue logs, and RFI trackers — open vs closed counts, overdue items, and week-over-week deltas. Use when preparing a recurring weekly coordination or project status report. Triggers on "weekly report", "status report", "week over week", "coordination summary", "báo cáo tuần", "tổng hợp trạng thái tuần".
status: scaffold
---

# Weekly Report — Báo cáo tuần (SCAFFOLD)

> ⚠️ **Scaffold** — mới có khung. Expand before relying on it.

Tổng hợp báo cáo trạng thái BIM/coordination hằng tuần từ clash register, issue
log, RFI tracker: open vs closed, quá hạn, biến động tuần.

## Phạm vi dự kiến / planned scope
- Nhận đầu ra từ `clash-report-analysis`, `acc-issue-register`, `rfi-tracker`.
- So sánh với snapshot tuần trước (week-over-week delta).
- Xuất tóm tắt gọn (Markdown/Excel) cho họp tuần.

## Việc cần làm / TODO
- [ ] Định dạng snapshot + cách lưu lịch sử tuần.
- [ ] Script tổng hợp đa nguồn + delta.

Liên quan / related: tất cả skill trong `project-management` và `bim-coordination`.
