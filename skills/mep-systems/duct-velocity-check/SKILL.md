---
name: duct-velocity-check
description: Check HVAC duct air velocity and aspect ratio from a duct schedule export — computes velocity from airflow and cross-section (rectangular W×H or round Ø), flags over-velocity (noise/pressure) and high aspect ratios, with configurable limits and airflow units (l/s, CFM, m3/h). Use when QA-ing duct sizing or reviewing an MEP duct schedule. Triggers on "duct velocity", "duct sizing", "aspect ratio", "air velocity check", "duct schedule QA", "kiểm tra vận tốc ống gió", "size ống gió".
---

# Duct Velocity Check — Kiểm vận tốc ống gió

Tính **vận tốc = lưu lượng / tiết diện** từ duct schedule và cờ ống **vượt vận
tốc** (ồn/áp cao) hay **tỷ lệ cạnh W:H** quá lớn (khó chế tạo, tổn thất áp). Hỗ
trợ ống chữ nhật (`W×H`) và tròn (`Ø`).
Computes duct velocity from airflow and cross-section and flags over-velocity
and excessive aspect ratios.

## Khi nào dùng / When to use
- Có duct schedule export (Revit/Excel: Duct ID, Width, Height/Diameter, Airflow).
- Cần soát sizing: chỗ nào vận tốc quá cao, tỷ lệ cạnh xấu, thiếu dữ liệu.

## Cách dùng / How to use
```bash
python scripts/check_duct.py <ducts.csv>
# đổi đơn vị lưu lượng + ghi đè ngưỡng:
python scripts/check_duct.py <ducts.csv> --airflow-unit cfm --rules limits.json
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/check_duct.py assets/sample_ducts.csv
```

## Ngưỡng mặc định / default limits (`--rules` JSON để ghi đè)
- `max_velocity`: 8.0 m/s (vượt → cờ đỏ OVER-VELOCITY).
- `warn_velocity`: 6.0 m/s (giữa warn & max → cảnh báo).
- `max_aspect`: 4.0 (W:H tối đa; vượt → cờ đỏ).
- `--airflow-unit`: `l/s` (mặc định), `cfm`, `m3/h`, `m3/s`.

## Đầu ra / Output
- Bảng mỗi duct: Size · Flow · **Vận tốc (m/s)** · **Aspect** · Status.
- Tổng số **vượt ngưỡng** (đỏ) và **cảnh báo** (vàng). Exit 1 nếu có vi phạm
  (dùng làm gate QA).

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `math`, `re`, `json`).
- Kích thước hiểu là **mm**; đọc `Width`/`Height`, `Diameter`, hoặc parse cột
  `Size` như `600x400` / `Ø400`. Ngưỡng chỉnh theo tiêu chuẩn dự án (main vs branch).
