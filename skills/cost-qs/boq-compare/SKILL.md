---
name: boq-compare
description: Compares two bills of quantities or quantity takeoffs (old vs new) keyed by item code or description, reporting added and removed items and quantity/value increases or decreases with delta and percent, plus total-amount movement. Use when reviewing what changed between two BoQ revisions or two takeoff runs. Triggers on "BoQ compare", "quantity change", "compare takeoff", "variance", "cost movement", "so sánh khối lượng", "biến động BoQ".
license: MIT
---

# BoQ Compare — So sánh khối lượng / bảng giá

So sánh hai bản BoQ / bảng khối lượng theo mã item (hoặc mô tả): item **thêm /
bớt**, khối lượng **tăng / giảm** kèm Δ và %, và **biến động tổng giá trị**.
Diff two BoQs / takeoffs keyed by item code (or description): added/removed
items, quantity/value change with delta & percent, and total-amount movement.

## Khi nào dùng / When to use
- Có hai phiên bản BoQ / bảng khối lượng (revision, hoặc hai lần bóc tách).
- Cần biết item nào mới/bỏ, khối lượng đổi bao nhiêu, tổng tiền dịch chuyển thế nào.

## Cách dùng / How to use
```bash
python scripts/compare_boq.py <old.csv> <new.csv>
# ép cột khoá + ghi diff CSV:
python scripts/compare_boq.py <old.csv> <new.csv> --key "Item" --csv out/boq_diff.csv
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/compare_boq.py assets/sample_boq_v1.csv assets/sample_boq_v2.csv
```

## Đầu ra / Output
- Tóm tắt: số item cũ/mới, **Added / Removed / Changed**.
- Danh sách item thêm/bớt; item đổi khối lượng (old → new, Δ, %).
- **Tổng giá trị** cũ → mới (Δ, %) nếu cả hai file có cột amount.
- (Tuỳ chọn) CSV diff: `key, change, description, old_qty, new_qty, delta, unit`.

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `re`).
- Khoá: tự dò cột mã (Item/Code/Ref) → nếu không có thì Description; ép bằng `--key`.
- Bỏ đơn vị & dấu phẩy khi so số. Kết hợp `quantity-takeoff` để tạo dữ liệu đầu vào.
