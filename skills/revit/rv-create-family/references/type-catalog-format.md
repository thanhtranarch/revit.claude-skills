# Revit Type Catalog — định dạng / format

Type catalog là file `.txt` đặt **cùng thư mục và cùng tên** với file family
(`Door.rfa` → `Door.txt`). Khi load family, Revit đọc catalog và cho chọn type
nào cần nạp — thay vì nạp hết mọi type.

## Cấu trúc / structure
- Phân tách bằng dấu **phẩy** (`,`). Không dùng dấu phẩy trong giá trị.
- **Dòng đầu**: ô đầu tiên **để trống**, rồi tới header từng cột tham số:
  ```
  ,Width##LENGTH##millimeters,Height##LENGTH##millimeters,Fire Rating##OTHER##
  ```
- **Mỗi dòng sau**: tên type + giá trị theo thứ tự cột:
  ```
  Single 900x2100,900,2100,60/60/60
  ```

## Header cột: `Name##TYPE##unit`
- `Name` — tên tham số, phải **khớp** tham số có trong family.
- `TYPE` — nhóm kiểu:
  - Dimensional (giá trị là **số**): `LENGTH`, `AREA`, `VOLUME`, `ANGLE`,
    `NUMBER`, `FORCE`, `MASS`, `CURRENCY`, `SLOPE`, `SPEED`…
  - Phi kích thước (text / yes-no / vật liệu…): `OTHER` (bỏ trống `unit`).
- `unit` — đơn vị cho kiểu dimensional: `millimeters`, `meters`, `square_meters`,
  `degrees`… Với `OTHER` để trống (`Fire Rating##OTHER##`).

## Script này / this skill
`scripts/build_type_catalog.py` đọc CSV (dòng = type, cột = tham số) và:
- Header cột có sẵn `##TYPE##unit` → dùng nguyên; không có → mặc định `##OTHER##`.
- Kiểm: trùng tên type, trùng tên cột, thiếu tên type, giá trị **không phải số**
  ở cột dimensional, và **dấu phẩy trong giá trị** (phá vỡ catalog).
- Xuất `.txt` đúng định dạng trên (`--catalog`) hoặc plan JSON (`--json`) cho
  template pyRevit tạo type trong family đang mở.

## Lưu ý / notes
- Giá trị dimensional trong catalog theo **đơn vị bạn khai ở header** (không phải
  đơn vị nội bộ Revit) — Revit tự quy đổi khi nạp.
- Yes/No: dùng `OTHER`, giá trị `1`/`0`.
- Kiểm bảng trước khi phát cho team để tránh type lỗi khi load family.
