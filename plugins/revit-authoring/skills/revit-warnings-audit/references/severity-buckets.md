# Severity buckets — phân mức warning

`parse_warnings.py` gán mức nghiêm trọng cho mỗi message theo từ khoá. Sửa danh
sách `HIGH_KEYWORDS` / `MEDIUM_KEYWORDS` trong script để hợp với chuẩn đội bạn.

## HIGH — ảnh hưởng dữ liệu/hình học, ưu tiên sửa
- `duplicate` — trùng Mark/Type Mark → sai schedule, sai thống kê.
- `identical instances` / `coincident` / `same location` → double counting.
- `overlap` (walls overlap) → sai room boundary/diện tích.
- `not enclosed` (room/area) → thiếu diện tích, sai báo cáo.
- `join` — lỗi nối phần tử.
- `instances of a group` — lệch group.

## MEDIUM — cảnh báo mô hình, nên xử lý
- `mismatch`, `type mark`, `mark value` không unique.
- `off axis`, `slightly` — hình học lệch nhẹ.
- `unconnected`, `no phase`, `out of date`.

## LOW — còn lại
- Các warning nhỏ/thẩm mỹ không rơi vào hai nhóm trên.

## Mẹo / tips
- Warning về `duplicate mark` thường nhiều nhất và đáng sửa sớm vì phá schedule.
- Theo dõi tổng warning + số HIGH qua từng tuần để thấy xu hướng model health.
- Kết hợp skill `revit-model-audit` để có checklist dọn dẹp tổng thể.
