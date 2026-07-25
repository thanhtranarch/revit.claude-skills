---
name: rfi-tracker
description: Tracks Requests for Information (RFIs) from a register — status, days open, ball-in-court, response due dates, aging buckets, and cost/schedule impact flags. Use when managing RFIs or producing an RFI status/aging report. Triggers on "RFI log", "RFI tracker", "RFI aging", "days open", "response due", "theo dõi RFI", "báo cáo RFI".
license: MIT
---

# RFI Tracker — Theo dõi & phân tích RFI

Theo dõi RFI từ register CSV: trạng thái, số ngày mở, ball-in-court, hạn phản
hồi, nhóm **aging** (0–7 / 8–14 / 15–30 / 31+ ngày), cờ ảnh hưởng chi phí/tiến
độ, và KPI thời gian phản hồi.
Track RFIs from a register: status, days open, ball-in-court, response due,
aging buckets, cost/schedule impact flags, and response-time KPIs.

## Khi nào dùng / When to use
- Có RFI register export (Procore/ACC/BIM360/Excel) dạng CSV.
- Cần: aging report, danh sách quá hạn phản hồi, ai đang giữ bóng (ball-in-court),
  bao nhiêu RFI ảnh hưởng chi phí/tiến độ, thời gian phản hồi trung bình.

## Cách dùng / How to use
```bash
python scripts/track_rfis.py <rfi_register.csv>
# đổi mốc so hạn + xuất register có cột tính toán:
python scripts/track_rfis.py <rfi_register.csv> --as-of 2026-07-24 --csv out/rfi_register.csv
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/track_rfis.py assets/sample_rfis.csv --as-of 2026-07-24
```

## Đầu ra / Output
- Tóm tắt: tổng / open / closed, đếm theo **status** và **ball-in-court**.
- **Aging** các RFI đang mở theo số ngày mở; danh sách **quá hạn phản hồi**.
- Số RFI có **cost impact** / **schedule impact**.
- KPI thời gian phản hồi của RFI đã đóng (trung bình / trung vị / max).
- (Tuỳ chọn) CSV register + cột `days_open`, `overdue`, `bucket`.

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `datetime`, `statistics`).
- Tự dò cột theo alias (xem `references/rfi-columns.md`). Cột thiếu để trống.
- RFI đã `Closed`/`Answered`/có ngày đóng không tính là quá hạn.
- Aging chỉ tính RFI đang mở; ngày mở = (ngày đóng hoặc mốc so hạn) − ngày gửi.
