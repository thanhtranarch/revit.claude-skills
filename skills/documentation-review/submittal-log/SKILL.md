---
name: submittal-log
description: Build and track a submittal log from spec sections and submittal registers — status (pending/under review/approved/rejected), ball-in-court, and overdue flags. Use when managing construction submittals or producing a submittal status report. Triggers on "submittal log", "submittal register", "ball in court", "submittal status", "nhật ký submittal", "theo dõi submittal".
status: scaffold
---

# Submittal Log — Nhật ký submittal (SCAFFOLD)

> ⚠️ **Scaffold** — mới có khung. Expand before relying on it.

Lập & theo dõi submittal log từ spec section + register: trạng thái, ball-in-court,
đánh dấu quá hạn.

## Phạm vi dự kiến / planned scope
- Chuẩn hoá submittal register (CSV) → log có trạng thái vòng đời.
- Ball-in-court (bên đang giữ), ngày nhận/trả, hạn.
- Báo cáo trạng thái + danh sách quá hạn (tái dùng logic overdue).

## Việc cần làm / TODO
- [ ] Schema submittal + trạng thái.
- [ ] Script tóm tắt + overdue (tham khảo `normalize_issues.py`).

Liên quan / related: `acc-issue-register`, `comment-aggregation`.
