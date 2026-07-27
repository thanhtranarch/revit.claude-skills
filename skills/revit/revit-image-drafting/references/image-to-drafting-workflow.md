# Image → Drafting View workflow — chèn & scale ảnh để trace

## Bước 1 — biết cỡ thật của ảnh
Cần **một kích thước thật** trên ảnh (vd tổng bề rộng công trình = 10 000 mm).
```bash
python scripts/image_scale.py sketch.png --real-width-mm 10000 --scale 100
```
Kết quả cho: kích thước px, DPI, và **Width/Height** cần đặt (mm) + cỡ in @1:100.

## Bước 2 — đặt ảnh trong Revit
**Cách A — thủ công:** View > Drafting View (đặt scale) → Insert > Image → chọn
ảnh → set **Width** = giá trị ở Bước 1 → khoá ảnh (Pin).

**Cách B — template pyRevit:** `templates/pyrevit_place_image_drafting_view.py`
- Đặt `IMAGE_PATH`, `VIEW_NAME`, `WIDTH_FT` (mm/304.8) rồi chạy trong pyRevit.
- Yêu cầu Revit **2022+** (API `ImageType.Create` / `ImageInstance.Create`);
  bản cũ hơn phải chèn thủ công.

## Bước 3 — trace
- Vẽ **detail line / filled region** đè lên ảnh (drafting view là 2D, không phải model).
- Nếu cần thành **model**: đo từ ảnh rồi dựng bằng skill `revit-cad-import` hoặc mô
  hình hoá trực tiếp — ảnh drafting view không tạo hình học model.
- Xong thì có thể **xoá ảnh** (giữ file nhẹ) — nét trace vẫn còn.

## Mẹo scale / scaling tips
- DPI trong file thường không đáng tin cho bản vẽ scan → luôn dùng `--real-width-mm`.
- Ảnh méo (không vuông pixel) → cắt/nắn ảnh trước khi đưa vào.
- Muốn ảnh in đúng cỡ giấy ở tỷ lệ 1:S → xem dòng "in trên sheet" trong output.

## Định dạng ảnh / formats
`image_scale.py` đọc **PNG, JPEG, GIF, BMP** bằng thư viện chuẩn (không cần
Pillow). PDF scan: tách trang thành ảnh trước (ngoài phạm vi skill này).
