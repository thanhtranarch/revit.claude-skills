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

## 1. 🟢 `comment-to-update-locations` — Comment → vị trí cần update ✅ *đã build*
**Nhóm:** `revit` · **category:** coordination ·
**skill:** [`skills/revit/comment-to-update-locations`](../skills/revit/comment-to-update-locations/SKILL.md).

Từ comment/markup review (Bluebeam CSV, ACC issues, RFI) → trích **vị trí cần cập
nhật** trong model (sheet / level / grid / room / Element ID) từ cột chuyên dụng
hoặc **parse text song ngữ EN/VI**, sinh **punch list** "ở đâu, sửa gì, ai làm".

- **Đã có (offline):** trích vị trí 2 lớp (cột + text), punch list theo ưu tiên,
  `--open-only`, CSV/JSON, cảnh báo comment chưa xác định được vị trí.
- **Còn để mở rộng (cần Revit MCP):** chọn/zoom đúng element theo ID, đổi
  grid/level → toạ độ thực trong model (nối với pyRevit `SelectElementsByIds`).
- **Kế thừa:** `bluebeam-pdf/comment-aggregation` (gộp nguồn) → thêm lớp *định vị*.

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

## 4. 🟢 `iso19650-project-audit` — Kiểm tra ISO 19650 toàn dự án ✅ *đã build*
**Nhóm:** `office-data` · **category:** standards ·
**skill:** [`skills/office-data/iso19650-project-audit`](../skills/office-data/iso19650-project-audit/SKILL.md).

Vượt khỏi *đặt tên file* (`iso19650-naming-check`): kiểm tra **mức độ tuân thủ
ISO 19650 của cả dự án** từ CDE register — metadata đầy đủ, mã suitability/revision
hợp lệ, ngày ISO 8601, **nhất quán trạng thái CDE ↔ suitability ↔ revision**, và
đối chiếu độ phủ **MIDP** — kèm scorecard %.

- **Đã có (offline):** 6 hạng mục kiểm + scorecard + `--expected` (MIDP) + `--rules`.
- **Còn để mở rộng:** LOIN/LOD, TIDP/MIDP đầy đủ, cấu trúc CDE thực tế vẫn cần
  người/BEP review (xem `references/iso19650-checklist.md`).
- **Kế thừa:** `iso19650-naming-check` (naming) + `cobie-validation` (handover data).

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
