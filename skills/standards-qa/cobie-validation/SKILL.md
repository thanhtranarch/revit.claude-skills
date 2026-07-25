---
name: cobie-validation
description: Validates a COBie sheet export (CSV) for completeness — required columns present, required cells non-empty, unique Name, CreatedBy is an email, and CreatedOn is a valid ISO 8601 date — for Facility, Floor, Space, Zone, Type, Component, and System sheets. Use when checking a COBie deliverable before handover or issuing an asset-information dataset. Triggers on "COBie", "COBie validation", "asset information", "handover data", "COBie completeness", "kiểm tra COBie", "dữ liệu bàn giao".
license: MIT
---

# COBie Validation — Kiểm tính đầy đủ COBie

Kiểm một sheet COBie (CSV export) trước bàn giao: đủ **cột bắt buộc**, ô bắt buộc
**không rỗng**, **Name** duy nhất, **CreatedBy** là email, **CreatedOn** đúng ISO
8601 — cho các sheet Facility, Floor, Space, Zone, Type, Component, System.
Validate a COBie sheet for completeness before handover.

## Khi nào dùng / When to use
- Có deliverable COBie (xuất từng sheet ra CSV) cần kiểm trước bàn giao/handover.
- Cần soát nhanh ô rỗng, Name trùng, email/ngày sai định dạng.

## Cách dùng / How to use
```bash
python scripts/check_cobie.py <sheet.csv> --sheet Component
# tự dò loại sheet theo header:
python scripts/check_cobie.py <sheet.csv>
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/check_cobie.py assets/sample_component.csv
```

## Sheet & cột bắt buộc / sheets & required columns
| Sheet | Cột bắt buộc |
|-------|--------------|
| Facility | Name, CreatedBy, CreatedOn, Category, ProjectName, SiteName, LinearUnits, AreaUnits, VolumeUnits |
| Floor / Type | Name, CreatedBy, CreatedOn, Category |
| Space | Name, CreatedBy, CreatedOn, Category, FloorName |
| Zone | Name, CreatedBy, CreatedOn, Category, SpaceNames |
| Component | Name, CreatedBy, CreatedOn, TypeName, Space |
| System | Name, CreatedBy, CreatedOn, Category, ComponentNames |

## Đầu ra / Output
- 🔴 lỗi: thiếu cột, ô bắt buộc rỗng, Name trùng.
- 🟡 cảnh báo: CreatedBy không phải email, CreatedOn không đúng ISO 8601.
- Tổng lỗi/cảnh báo; exit 1 nếu có lỗi (gate trước bàn giao).

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `re`, `datetime`).
- COBie yêu cầu ô không áp dụng ghi **`n/a`** (không để trống).
- Đây là kiểm **completeness** cấp sheet; chưa kiểm tham chiếu chéo giữa các sheet
  (vd Component.Space phải tồn tại trong Space) — bước đó cần bộ nhiều sheet.
