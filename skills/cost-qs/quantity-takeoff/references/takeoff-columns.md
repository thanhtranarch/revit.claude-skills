# Takeoff columns — alias mapping

`takeoff.py` tự dò cột theo tên (không phân biệt hoa/thường).

## Cột nhóm / group column (mặc định)
`Category`, `Cat`, `Group`, `Family`, `Type`, `Assembly`, `Element Type`,
`Family and Type`. Ép bằng `--group-by "Tên cột"`.

## Cột khối lượng / quantity columns
| Khoá / key | Alias header |
|------------|--------------|
| `count` | Count, Qty, Quantity, Nos, No., Number, Pcs, Each |
| `area` | Area, Gross Area, Net Area, Surface Area, Floor Area |
| `volume` | Volume, Gross Volume, Net Volume |
| `length` | Length, Len, Perimeter, Run, Linear |
| `weight` | Weight, Mass |

Chỉ cột **có mặt** trong file mới được cộng & hiển thị.

## Xử lý số / number handling
- Bỏ mọi ký tự không phải số/`.`/`-` (kể cả đơn vị `m²`, `m³`, `kg`) và dấu phẩy
  nghìn trước khi cộng.
- Ô rỗng/không phải số → bỏ qua (không cộng), không làm hỏng tổng nhóm.

## Xuất từ Revit / exporting from Revit
- Tạo **Schedule** theo category, bật các cột số lượng cần (Count/Area/Volume/
  Length), **Export** → CSV.
- Giữ đơn vị nhất quán (vd toàn m²/m³) để tổng có nghĩa; công cụ không đổi đơn vị.
