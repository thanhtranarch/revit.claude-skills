---
name: change-order-log
description: Track construction change orders / variations from a register — status (pending/approved/rejected), cost and schedule impact, running totals by status and discipline, aging, and overdue-decision flags. Use when managing change orders, variations, or PCOs and needing a cost-impact rollup or an overdue-approval list. Triggers on "change order log", "variation register", "CO tracker", "cost impact", "PCO", "nhật ký change order", "theo dõi biến động chi phí".
---

# Change Order Log — Theo dõi change order / variation

Theo dõi change order (variation/PCO) từ register CSV: trạng thái, **ảnh hưởng
chi phí & tiến độ**, tổng giá trị theo trạng thái và bộ môn, aging, cờ quá hạn
quyết định.
Track change orders from a register: status, cost & schedule impact, running
totals by status and discipline, aging, and overdue-decision flags.

## Khi nào dùng / When to use
- Có change-order / variation register (CSV) từ Procore/ACC/Excel.
- Cần: tổng giá trị đã duyệt / đang chờ / bị từ chối, giá trị theo bộ môn,
  danh sách CO quá hạn quyết định, số ngày tiến độ được duyệt.

## Cách dùng / How to use
```bash
python scripts/track_change_orders.py <change_orders.csv>
python scripts/track_change_orders.py <change_orders.csv> --as-of 2026-07-24 --csv out/co_register.csv
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/track_change_orders.py assets/sample_change_orders.csv --as-of 2026-07-24
```

## Đầu ra / Output
- Đếm theo trạng thái; phân loại **approved / pending / rejected**.
- **Giá trị chạy dồn**: submitted / approved / pending / rejected + số ngày tiến độ duyệt.
- Giá trị theo **bộ môn**.
- Danh sách CO **quá hạn quyết định** (kèm số ngày & giá trị).
- (Tuỳ chọn) CSV register + cột `cost_value`, `sched_value`, `bucket`, `days_open`, `overdue`.

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `datetime`, `re`).
- Tiền tệ nhận `$12,500`, `12500`, ngoặc `(30,000)` = âm (deductive).
- `approved`/`approved as noted`/`accepted` = duyệt; `rejected`/`declined`/`void`/
  `withdrawn` = từ chối; còn lại = đang chờ. Chỉ CO đang chờ mới tính quá hạn.
