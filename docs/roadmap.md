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

## 1. 🟢 `rv-comment-locations` — Comment → vị trí cần update ✅ *đã build*
**Nhóm:** `revit` · **category:** coordination ·
**skill:** [`skills/revit/rv-comment-locations`](../skills/revit/rv-comment-locations/SKILL.md).

Từ comment/markup review (Bluebeam CSV, ACC issues, RFI) → trích **vị trí cần cập
nhật** trong model (sheet / level / grid / room / Element ID) từ cột chuyên dụng
hoặc **parse text song ngữ EN/VI**, sinh **punch list** "ở đâu, sửa gì, ai làm".

- **Đã có (offline):** trích vị trí 2 lớp (cột + text), punch list theo ưu tiên,
  `--open-only`, CSV/JSON, cảnh báo comment chưa xác định được vị trí.
- **Còn để mở rộng (cần Revit MCP):** chọn/zoom đúng element theo ID, đổi
  grid/level → toạ độ thực trong model (nối với pyRevit `SelectElementsByIds`).
- **Kế thừa:** `bluebeam-pdf/comment-aggregation` (gộp nguồn) → thêm lớp *định vị*.

## 2. 🟢 `rv-family-image` — Dựng Revit Family từ hình ảnh ✅ *đã thêm*
**Nhóm:** `revit` · **discipline:** multi · **category:** automation ·
**skill:** [`skills/revit/rv-family-image`](../skills/revit/rv-family-image/SKILL.md) ·
**cần Revit MCP:** ✅ (T3Lab_Lite JSONtoFamily).

Từ **ảnh tham chiếu** (đồ nội thất, thiết bị, cấu kiện) → sinh **Revit Family
(.rfa)**: phân tích ảnh → JSON mô tả hình học/param → tạo family qua MCP.

- **In:** 1 ảnh (+ kích thước/loại nếu có). **Out:** `.rfa` + JSON mô tả.
- **Đã có:** repo-hoá từ tooling **T3Lab JSONtoFamily**, khai báo `compatibility` rõ.
- **Còn để mở rộng:** spec/kiểm hình học, test tự động.
- ⚠️ *Cần ảnh đầu vào cụ thể để chạy thật.*

## 3. 🟢 `rvstr-beam-cad` · `rvstr-column-tools` — CAD → cấu kiện Kết cấu ✅ *đã thêm*
**Nhóm:** `revit` · **discipline:** structural · **category:** automation ·
**skills:** [`rvstr-beam-cad`](../skills/revit/rvstr-beam-cad/SKILL.md),
[`rvstr-column-tools`](../skills/revit/rvstr-column-tools/SKILL.md) · **cần Revit MCP:** ✅.

Từ **DWG/CAD đã import** → dựng/hiệu chỉnh cấu kiện Revit kết cấu (beam, column,
grid) theo layer/nét: đọc CAD → ghép nét → đặt phần tử qua MCP (trong `Transaction`).

- `rvstr-beam-cad`: ghép cặp nét song song → centerline → tạo Structural Beam + type, z-offset.
- `rvstr-column-tools`: replace wall→column, extract toạ độ (snap grid), dim-to-grid.
- **Còn để mở rộng:** nhận diện từ **ảnh mặt bằng**; kiểm rotation/độ phủ; mở rộng
  sang Kiến trúc (prefix `rvarc-`).

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
