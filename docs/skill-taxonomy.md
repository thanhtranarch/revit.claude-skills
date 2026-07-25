# Skill Taxonomy — Bản đồ các bộ skill / Skill set map

Tất cả skill nằm trong `skills/<bộ>/<tên-skill>/SKILL.md`. Mỗi **bộ (set)** gom
skill theo lĩnh vực công việc trong ngành ACE/AEC.

## Quy ước đặt tên / naming conventions
- Thư mục skill = **kebab-case**, duy nhất trong repo (vd `clash-report-analysis`).
- `name` trong frontmatter **phải khớp** tên thư mục.
- `description` nêu rõ *skill làm gì* + *khi nào dùng* + *từ khoá kích hoạt*
  (song ngữ nếu có thể) để Claude chọn đúng skill.
- Cấu trúc bên trong (tuỳ nhu cầu): `scripts/`, `references/`, `assets/`,
  `templates/`.
- Skill chưa hoàn thiện đặt `status: scaffold` trong frontmatter.

## Bảy bộ hiện có / seven sets

### 1. `bim-coordination` — Coordination & Clash
| Skill | Trạng thái | Mô tả ngắn |
|-------|-----------|------------|
| `clash-report-analysis` | ✅ chạy được | Phân tích/tóm tắt report clash Navisworks (XML) |
| `shared-coordinates` | ✅ hướng dẫn+script | Thiết lập & QA toạ độ chung; so SP/PBP/north giữa model |
| `model-federation` | ✅ hướng dẫn+script | Gộp model coordination (NWF/NWD, ACC) + check readiness |
| `coordination-issue-log` | ✅ chạy được | Gộp clash nhiều vòng → issue log + export import ACC |

### 2. `revit-authoring` — Revit / Dynamo / pyRevit
Bộ đầy đủ — xem [`skills/revit-authoring/README.md`](../skills/revit-authoring/README.md)
để biết cách cài đặt.

| Skill | Trạng thái | Mô tả ngắn |
|-------|-----------|------------|
| `dynamo-pyrevit-helper` | ✅ mẫu+ref | Viết/rà soát script pyRevit & Dynamo |
| `family-parameter-management` | ✅ chạy được | Phân tích shared parameter file (GUID/tên trùng, thiếu mô tả) |
| `schedule-qa` | ✅ chạy được | Validate schedule CSV theo rules (required/unique/allowed) |
| `revit-warnings-audit` | ✅ chạy được | Gom nhóm & ưu tiên warning từ HTML export |
| `revit-model-audit` | ✅ hướng dẫn+script | Checklist + scorer sức khoẻ model (🔴/🟡/🟢 + health index) |
| `revit-batch-export` | ✅ mẫu+ref | Export hàng loạt sheet ra PDF/DWG/NWC/IFC theo tên chuẩn |
| `family-naming-audit` | ✅ chạy được | Kiểm tên family/type theo chuẩn; bắt trùng & dùng lại category |
| `model-compare` | ✅ chạy được | So 2 phiên bản model: added/deleted/changed theo Element ID |

### 3. `documentation-review` — Tài liệu / Markup / Comment
| Skill | Trạng thái | Mô tả ngắn |
|-------|-----------|------------|
| `pdf-markup-compare` | ✅ chạy được | So sánh markup giữa 2 revision PDF |
| `comment-aggregation` | ✅ chạy được | Gộp comment/RFI nhiều nguồn → Excel register |
| `submittal-log` | ✅ chạy được | Nhật ký & trạng thái submittal, ball-in-court, review cycle |
| `drawing-register-qa` | ✅ chạy được | QA sổ phát hành: revision/suitability/ngày, trùng số |

### 4. `project-management` — ACC/BIM360 + Excel
| Skill | Trạng thái | Mô tả ngắn |
|-------|-----------|------------|
| `acc-issue-register` | ✅ chạy được | Chuẩn hoá issue ACC/BIM360 + overdue |
| `rfi-tracker` | ✅ chạy được | Theo dõi RFI + aging, ball-in-court, KPI phản hồi |
| `weekly-report` | ✅ chạy được | Báo cáo trạng thái tuần đa nguồn + Δ tuần |
| `change-order-log` | ✅ chạy được | Theo dõi change order: giá trị approved/pending/rejected, quá hạn |
| `action-item-tracker` | ✅ chạy được | Theo dõi action item họp: owner, aging, overdue |
| `risk-register` | ✅ chạy được | Chấm điểm P×I, RAG, review quá hạn, top rủi ro |

### 5. `standards-qa` — Chuẩn & QA tài liệu/dữ liệu
Bộ đầy đủ — xem [`skills/standards-qa/README.md`](../skills/standards-qa/README.md).

| Skill | Trạng thái | Mô tả ngắn |
|-------|-----------|------------|
| `iso19650-naming-check` | ✅ chạy được | Kiểm tên file theo ISO 19650 (trường, Type/Role, status/revision) |
| `spellcheck-review` | ✅ chạy được | Soát chính tả text AEC (lỗi thường gặp + từ lặp; `--dict` tuỳ chọn) |
| `sheet-naming-check` | ✅ chạy được | Kiểm chuẩn số/tên sheet, bắt trùng số & từ cấm trong tên |
| `cobie-validation` | ✅ chạy được | Kiểm tính đầy đủ sheet COBie (cột bắt buộc, ô rỗng, Name trùng) |

### 6. `cost-qs` — Bóc tách khối lượng & chi phí
Bộ đầy đủ — xem [`skills/cost-qs/README.md`](../skills/cost-qs/README.md).

| Skill | Trạng thái | Mô tả ngắn |
|-------|-----------|------------|
| `quantity-takeoff` | ✅ chạy được | Gom & cộng khối lượng theo nhóm (count/area/volume/length/weight) |
| `boq-compare` | ✅ chạy được | So 2 bản BoQ/takeoff: item thêm/bớt, Δ khối lượng & tổng giá trị |

### 7. `mep-systems` — Kiểm tra hệ thống MEP
Bộ đầy đủ — xem [`skills/mep-systems/README.md`](../skills/mep-systems/README.md).

| Skill | Trạng thái | Mô tả ngắn |
|-------|-----------|------------|
| `duct-velocity-check` | ✅ chạy được | Vận tốc & tỷ lệ cạnh ống gió; cờ vượt vận tốc / aspect |

## Mở rộng / how to grow
1. Thêm bộ mới = thư mục con của `skills/` (vd `mep-systems`, `cost-qs`, `gis-civil`).
2. Thêm skill = tạo thư mục + `SKILL.md` (copy `templates/SKILL_TEMPLATE.md`).
3. Ưu tiên skill **có script chạy được** khi có thể; nếu không, làm skill hướng
   dẫn/checklist rõ ràng.
4. Chạy `validate_skill.py` + `audit_skill.py` trước khi mở PR (xem
   `docs/security-model.md`).

## Ý tưởng bộ tương lai / future sets (chưa tạo)
- `gis-civil` — Civil 3D, surface, corridor, toạ độ khảo sát.
- Mở rộng `mep-systems` — pipe sizing, equipment schedule QA, connected load.
- Mở rộng `cost-qs` — dự toán (rate build-up), cash flow / S-curve.
- Mở rộng `standards-qa` — BS 1192, layer standards, tham chiếu chéo COBie giữa sheet.
