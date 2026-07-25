# Roadmap — Phát triển skill Revit / Revit skill roadmap

Lộ trình mở rộng **nhóm `skills/revit/`** theo hướng tự động hoá sâu hơn: từ
*đọc dữ liệu* (các skill hiện tại chạy trên export CSV/HTML) tiến tới *tác động
model* qua **Revit MCP / pyRevit / Dynamo**.
Roadmap for growing the `revit/` group from read-only data skills toward
model-authoring skills driven by a Revit MCP / pyRevit / Dynamo connector.

> **Ghi chú kiến trúc / architecture note.** Skill hiện có trong repo là bộ xử lý
> **offline** (chỉ stdlib + pyyaml/pandas, chạy trên file export). Các skill dưới
> đây cần **ghi vào Revit**, nên phụ thuộc **Revit MCP connector** (vd. T3Lab)
> — chúng sẽ là skill *hướng-MCP*, khác nhóm skill offline. Mỗi mục đánh dấu phụ
> thuộc rõ ràng.

Trạng thái: 🟡 *planned* · 🟠 *scaffold* · 🟢 *runnable*

---

## 1. 🟡 `comment-to-update-locations` — Comment → vị trí cần update
**Nhóm:** `revit` · **category:** documentation · **cần Revit MCP:** một phần
(đọc model để map).

Từ comment/markup review (Bluebeam CSV, ACC issues, RFI) → trích **vị trí/phần tử
cần cập nhật** trong model: map comment về Element ID / grid / toạ độ / sheet,
sinh **punch list** "ở đâu, sửa gì, ai làm".

- **In:** comment/markup export (dựa trên `bluebeam-pdf/comment-aggregation`,
  `acc-bim360/acc-issue-register`) + tuỳ chọn export phần tử từ Revit.
- **Out:** bảng `element_id | grid | level | sheet | comment | action | owner`.
- **Kế thừa:** `comment-aggregation` (gộp) → thêm lớp *định vị trong model*.

## 2. 🟡 `image-to-family` — Dựng Revit Family từ hình ảnh
**Nhóm:** `revit` · **category:** automation · **cần Revit MCP:** ✅ (JSONtoFamily).

Từ **ảnh tham chiếu** (đồ nội thất, thiết bị, cấu kiện) → sinh **Revit Family
(.rfa)**: phân tích ảnh → JSON mô tả hình học/param → tạo family qua MCP.

- **In:** 1 ảnh (+ kích thước/loại nếu có).
- **Out:** `.rfa` + JSON mô tả.
- **Kế thừa:** đã có tooling **T3Lab JSONtoFamily** qua MCP Revit (skill cá nhân
  `revit-family-from-image`) → mục tiêu là bản **repo-hoá** có script/spec rõ,
  test được, kèm quy tắc an toàn.
- ⚠️ *Cần ảnh đầu vào cụ thể để chạy thật; hiện chưa có ảnh nào được cung cấp.*

## 3. 🟡 `cad-to-model` — Ảnh / CAD → dựng lại công trình
**Nhóm:** `revit` · **category:** automation · **cần Revit MCP:** ✅.

Từ **DWG/CAD hoặc ảnh mặt bằng** → dựng lại cấu kiện Revit (wall, column, beam,
grid) theo layer/nét: đọc CAD → nhận diện đối tượng → đặt phần tử qua MCP.

- **In:** DWG đã import (layer beam/column/wall) hoặc ảnh mặt bằng có tỉ lệ.
- **Out:** phần tử Revit (structural/architectural) + log đối chiếu.
- **Kế thừa:** tooling sẵn có `revit-beam-from-cad`, `revit-column-tools` (T3Lab)
  → repo-hoá thành skill có quy trình + kiểm tra (pairing nét, z-offset, rotation…).

## 4. 🟡 `iso19650-project-audit` — Kiểm tra ISO 19650 toàn dự án
**Nhóm:** `office-data` (mở rộng sang `revit` nếu đọc model) · **category:** standards.

Vượt khỏi *đặt tên file* (`iso19650-naming-check`): kiểm tra **mức độ tuân thủ
ISO 19650 của cả dự án** so với chuẩn BIM đã cam kết (BEP/EIR): cấu trúc CDE,
mã suitability/status theo giai đoạn, metadata container, LOIN/LOD, ma trận trách
nhiệm (TIDP/MIDP), tính đầy đủ thông tin bàn giao.

- **In:** file register/CDE export + checklist chuẩn dự án (BEP/EIR).
- **Out:** báo cáo *đạt/chưa đạt* theo từng yêu cầu ISO 19650, %, danh sách thiếu.
- **Kế thừa:** `iso19650-naming-check` (naming) + `cobie-validation` (handover data)
  → nâng thành **audit toàn diện** cấp dự án.

---

## Nguyên tắc khi hiện thực / build principles
1. Skill offline (đọc/kiểm tra) → giữ chuẩn hiện tại: stdlib + `requirements.txt`,
   có `assets/` mẫu, validate + audit PASS.
2. Skill hướng-MCP (ghi vào Revit) → khai báo rõ `compatibility` (vd. *Requires
   Revit MCP connector*) trong frontmatter; **không** nhúng thao tác phá huỷ; ưu
   tiên đọc trước khi ghi; mọi thay đổi model bọc trong `Transaction`.
3. Gắn đủ `metadata` (`software`/`discipline`/`category`) và chạy
   `scripts/build_taxonomy.py` để skill mới hiện trong 3 bảng tra cứu.

*Thứ tự ưu tiên do bạn chốt — xem phần trao đổi để chọn skill làm trước.*
