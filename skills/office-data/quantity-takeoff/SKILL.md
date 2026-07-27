---
name: quantity-takeoff
description: Aggregates a quantity takeoff (QTO) from a Revit or Excel schedule export — grouping by category/family/type and summing count, area, volume, length, and weight columns, stripping units and thousands separators. Use when producing a takeoff, a BoQ starting point, or quantity totals by group from a schedule CSV. Triggers on "quantity takeoff", "QTO", "bill of quantities", "sum by category", "bóc tách khối lượng", "tổng khối lượng theo nhóm".
license: MIT
metadata:
  software: office-data
  discipline: multi
  category: cost
---

# Quantity Takeoff — Bóc tách khối lượng

Gom & cộng khối lượng từ schedule export (Revit/Excel): nhóm theo
category/family/type và cộng các cột **count / area / volume / length / weight**,
tự bỏ đơn vị (`m²`, `m³`, `m`, `kg`) và dấu phẩy nghìn.
Aggregate a quantity takeoff from a schedule export: group by a column and sum
the detected quantity columns.

## Khi nào dùng / When to use
- Có schedule export (Revit: Schedule → Export CSV; hoặc Excel) cần tổng khối lượng.
- Cần bảng bóc tách theo nhóm làm cơ sở cho BoQ / dự toán.

## Cách dùng / How to use
```bash
python scripts/takeoff.py <schedule.csv>
# nhóm theo cột khác + xuất CSV:
python scripts/takeoff.py <schedule.csv> --group-by Type --csv out/takeoff.csv
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/takeoff.py assets/sample_quantities.csv
```

## Đầu ra / Output
- Bảng theo nhóm: số dòng + tổng **Count / Area / Volume / Length / Weight**
  (chỉ hiện cột phát hiện được), kèm dòng **TỔNG / TOTAL**.
- (Tuỳ chọn) CSV bảng takeoff.

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `re`).
- Tự dò cột nhóm (Category/Family/Type…) và cột khối lượng theo alias; ép cột nhóm
  bằng `--group-by`.
- Bỏ đơn vị & dấu phẩy khi cộng (vd `1,250.50 m²` → 1250.50). Đơn vị do bạn giữ
  nhất quán ở nguồn — kết hợp `boq-compare` để so hai lần bóc tách.
