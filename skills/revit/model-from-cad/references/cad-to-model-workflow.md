# CAD → Model workflow — dựng model từ hình vẽ

Quy trình bán tự động: kiểm kê CAD bằng `parse_dxf.py`, sinh **build plan JSON**,
rồi dùng template pyRevit/Dynamo tạo phần tử. Con người vẫn duyệt & tinh chỉnh.

## Bước 1 — chuẩn bị DXF
- Trong CAD: `SAVEAS` → **AutoCAD DXF (ASCII)** (không phải DXF nhị phân/DWG).
- Đảm bảo **layer đặt tên rõ**: `WALL`, `COLUMN`, `GRID`, `DOOR`… (script gợi ý
  phần tử theo tên layer — kể cả tiếng Việt: `TUONG`, `COT`, `DAM`, `TRUC`).
- Đơn vị bản vẽ nên là **mm** (template đổi mm→ft cho Revit).

## Bước 2 — kiểm kê & xuất plan
```bash
python scripts/parse_dxf.py plan.dxf                 # bảng tổng quan
python scripts/parse_dxf.py plan.dxf --json > plan.json   # build plan cho template
```
`plan.json` chứa mỗi layer: `suggested_element`, `counts`, `length`,
**`segments`** (line → cho Wall/Beam/Grid) và **`points`** (block → cho Column).

## Bước 3 — tạo phần tử trong Revit
- **Tường** (pyRevit): sửa `PLAN`, `LAYER`, `WALL_HEIGHT_FT` trong
  `templates/pyrevit_walls_from_lines.py` rồi chạy trong pyRevit.
- **Cột** (Dynamo): node Python `templates/dynamo_columns_from_points.py`,
  `IN[0]=plan.json`, `IN[1]="COLUMN"`.
- Nguyên tắc: template dùng **loại đầu tiên** tìm được (WallType/FamilySymbol) và
  **level đầu tiên** — đổi theo dự án (lọc theo tên) trước khi chạy hàng loạt.

## Bước 4 — QA sau khi dựng
- Kiểm bằng `revit-warnings-audit` (overlap/duplicate) và `revit-model-audit`.
- Đối chiếu số phần tử tạo ra với `counts` trong plan.
- Nối tường ở góc, gán lại wall type/level đúng, kiểm cao độ.

## Giới hạn / limitations
- Chỉ đọc **DXF ASCII**; DWG/DXF nhị phân cần convert trước.
- Line cong (ARC/SPLINE) chưa sinh segment thẳng — xử lý riêng.
- Đây là bước **tăng tốc**, không thay thế mô hình hoá có kiểm soát: luôn duyệt
  kết quả. Template không đọc secret, không gọi mạng.
