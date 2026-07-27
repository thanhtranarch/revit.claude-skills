# Model Federation Checklist — gộp model coordination

Theo thứ tự. Mỗi mục: **việc làm** · **vì sao** · **ngưỡng/quy ước**.

## 1. Chuẩn bị toạ độ & đơn vị / coordinates & units
- Mọi model **Acquire Coordinates** từ một model chủ (site/kiến trúc) — xem skill
  `revit-shared-coordinates`.
- Đơn vị dự án thống nhất (thường **mm**); tránh model mét lẫn milimét.
- Chạy `check_model_list.py` để bắt lệch đơn vị/toạ độ trước khi append.

## 2. Quy ước tên & cấu trúc file / naming & structure
- Tên nhất quán: `<Dự án>-<Bộ môn>-<Khối/Zone>.<rvt|nwc>` (theo BEP).
- Xuất **NWC** từ từng model bộ môn (Navisworks exporter) ở vị trí cố định.
- **NWF** = file host tham chiếu các NWC (refresh được). **NWD** = ảnh chụp phát hành.

## 3. Thứ tự append / append order
- Append theo bộ môn nhất quán (vd: AR → ST → ME → EL → PL → CI).
- Giữ mỗi nguồn là một item để bật/tắt & gán selection set theo bộ môn.
- Không "merge" phá cấu trúc — cần giữ khả năng refresh từng nguồn.

## 4. Quy trình refresh / refresh workflow
- Khi model bộ môn cập nhật → re-export NWC (cùng tên/đường dẫn) → **Refresh** trong NWF.
- Ghi lại `last_updated` mỗi model; coi >7 ngày là **stale** (điều chỉnh theo dự án).
- Trước mỗi vòng clash: refresh tất cả, xác nhận không model nào stale.

## 5. Checklist "sẵn sàng clash" / clash-ready
- [ ] Cùng shared coordinates (link khớp, không lệch/xoay).
- [ ] Cùng đơn vị.
- [ ] Model mới nhất (không stale).
- [ ] Selection/Search sets theo bộ môn để lập ma trận clash có nghĩa.
- [ ] Loại trừ đối tượng nhiễu (đường tim, phòng, khối tích) khỏi clash hình học.

## 6. ACC Model Coordination (thay cho Navisworks)
- Upload model bộ môn vào thư mục **Coordination Space**; ACC tự tạo clash.
- Vẫn cần shared coordinates & đơn vị thống nhất.
- Kết quả clash → gán thành **Issues** (xem `coordination-issue-log`).

---
Kết hợp: `revit-shared-coordinates` → `model-federation` → `clash-report-analysis` →
`coordination-issue-log`.
