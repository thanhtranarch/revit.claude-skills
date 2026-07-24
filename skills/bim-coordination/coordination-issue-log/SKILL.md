---
name: coordination-issue-log
description: Turn clash results and coordination-meeting findings into a tracked issue log with owner, discipline, status, and target date, ready to push to ACC/BIM360 Issues. Use when running coordination meetings and needing to assign and track clash/coordination items over time. Triggers on "coordination log", "clash issue log", "assign clashes", "coordination meeting", "nhật ký coordination", "giao clash".
status: scaffold
---

# Coordination Issue Log — Nhật ký issue coordination (SCAFFOLD)

> ⚠️ **Scaffold** — mới có khung. Expand before relying on it.

Biến kết quả clash + phát hiện họp coordination thành nhật ký issue có người
phụ trách, bộ môn, trạng thái, hạn — sẵn sàng đẩy lên ACC/BIM360 Issues.

## Phạm vi dự kiến / planned scope
- Chuẩn hoá đầu vào từ `clash-report-analysis` (CSV register).
- Gán owner/discipline/target date; theo dõi trạng thái qua các vòng họp.
- Mẫu export khớp cột import Issues của ACC/BIM360.

## Việc cần làm / TODO
- [ ] Định nghĩa schema issue log + trạng thái vòng đời.
- [ ] Script gộp clash register nhiều vòng, giữ lịch sử.
- [ ] Mapping cột sang ACC import.

Liên quan / related: `clash-report-analysis`, `acc-issue-register`.
