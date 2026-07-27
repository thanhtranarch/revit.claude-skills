---
name: rfi-tracker
description: Track Requests for Information (RFIs) from a register — status, days open, ball-in-court, response due dates, and cost/schedule impact flags. Use when managing RFIs or producing an RFI status/aging report. Triggers on "RFI log", "RFI tracker", "RFI aging", "days open", "response due", "theo dõi RFI", "báo cáo RFI".
status: scaffold
---

# RFI Tracker — Theo dõi RFI (SCAFFOLD)

> ⚠️ **Scaffold** — mới có khung. Expand before relying on it.

Theo dõi RFI từ register: trạng thái, số ngày mở, ball-in-court, hạn phản hồi,
cờ ảnh hưởng chi phí/tiến độ.

## Phạm vi dự kiến / planned scope
- Chuẩn hoá RFI register (CSV) → tính days-open, aging bucket.
- Đánh dấu quá hạn phản hồi; nhóm theo bên phụ trách.
- Báo cáo aging (0–7, 8–14, 15+ ngày).

## Việc cần làm / TODO
- [ ] Script aging + overdue (tham khảo `normalize_issues.py`).
- [ ] Reference cột RFI phổ biến (Procore/ACC/BIM360).

Liên quan / related: `acc-issue-register`, `comment-aggregation`.
