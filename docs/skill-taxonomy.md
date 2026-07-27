# Skill Taxonomy — Bản đồ các bộ skill / Skill set map

Repo là một **plugin marketplace** của Claude Code. Mỗi **bộ (set)** = một
**plugin** trong `plugins/<bộ>/`; skill nằm trong `plugins/<bộ>/skills/<tên-skill>/SKILL.md`.
Marketplace liệt kê ở `.claude-plugin/marketplace.json`; mỗi plugin có
`.claude-plugin/plugin.json`. Skill được gọi dạng `/<bộ>:<tên-skill>`.

## Quy ước đặt tên / naming conventions
- Thư mục skill = **kebab-case**, duy nhất trong plugin (vd `clash-report-analysis`).
- `name` trong frontmatter **phải khớp** tên thư mục.
- `description` nêu rõ *skill làm gì* + *khi nào dùng* + *từ khoá kích hoạt*
  (song ngữ nếu có thể) để Claude chọn đúng skill.
- Cấu trúc bên trong (tuỳ nhu cầu): `scripts/`, `references/`, `assets/`,
  `templates/`.
- Skill chưa hoàn thiện đặt `status: scaffold` trong frontmatter.

## Năm plugin hiện có / five plugins

### 1. `bim-coordination` — Coordination & Clash
| Skill | Trạng thái | Mô tả ngắn |
|-------|-----------|------------|
| `clash-report-analysis` | ✅ chạy được | Phân tích/tóm tắt report clash Navisworks (XML) |
| `shared-coordinates` | ✅ hướng dẫn | Thiết lập & QA toạ độ chung (SP/PBP/north) |
| `model-federation` | 🚧 scaffold | Gộp model coordination (NWF/NWD, ACC) |
| `coordination-issue-log` | 🚧 scaffold | Biến clash thành issue log giao việc |

### 2. `revit-authoring` — Revit / Dynamo / pyRevit
Bộ đầy đủ — xem [`plugins/revit-authoring/README.md`](../plugins/revit-authoring/README.md)
để biết cách cài đặt.

| Skill | Trạng thái | Mô tả ngắn |
|-------|-----------|------------|
| `revit-dynamo-pyrevit-helper` | ✅ mẫu+ref | Viết/rà soát script pyRevit & Dynamo |
| `revit-family-parameter-management` | ✅ chạy được | Phân tích shared parameter file (GUID/tên trùng, thiếu mô tả) |
| `revit-schedule-qa` | ✅ chạy được | Validate schedule CSV theo rules (required/unique/allowed) |
| `revit-warnings-audit` | ✅ chạy được | Gom nhóm & ưu tiên warning từ HTML export |
| `revit-model-audit` | ✅ hướng dẫn | Checklist sức khoẻ model (file size, purge, CAD…) |
| `revit-batch-export` | ✅ mẫu+ref | Export hàng loạt sheet ra PDF/DWG/NWC/IFC theo tên chuẩn |

### 3. `documentation-review` — Tài liệu / Markup / Comment
| Skill | Trạng thái | Mô tả ngắn |
|-------|-----------|------------|
| `pdf-markup-compare` | ✅ chạy được | So sánh markup giữa 2 revision PDF |
| `comment-aggregation` | ✅ chạy được | Gộp comment/RFI nhiều nguồn → Excel register |
| `submittal-log` | 🚧 scaffold | Nhật ký & trạng thái submittal |

### 4. `project-management` — ACC/BIM360 + Excel
| Skill | Trạng thái | Mô tả ngắn |
|-------|-----------|------------|
| `acc-issue-register` | ✅ chạy được | Chuẩn hoá issue ACC/BIM360 + overdue |
| `rfi-tracker` | 🚧 scaffold | Theo dõi RFI + aging |
| `weekly-report` | 🚧 scaffold | Báo cáo trạng thái tuần đa nguồn |

### 5. `standards-qa` — Chuẩn & QA tài liệu/dữ liệu
Bộ đầy đủ — xem [`plugins/standards-qa/README.md`](../plugins/standards-qa/README.md).

| Skill | Trạng thái | Mô tả ngắn |
|-------|-----------|------------|
| `iso19650-naming-check` | ✅ chạy được | Kiểm tên file theo ISO 19650 (trường, Type/Role, status/revision) |
| `spellcheck-review` | ✅ chạy được | Soát chính tả text AEC (lỗi thường gặp + từ lặp; `--dict` tuỳ chọn) |
| `sheet-naming-check` | 🚧 scaffold | Kiểm chuẩn số/tên sheet & view, bắt trùng số |

## Mở rộng / how to grow
1. Thêm bộ mới = plugin mới trong `plugins/` (vd `mep-systems`, `cost-qs`,
   `gis-civil`): tạo `plugins/<bộ>/.claude-plugin/plugin.json` + `skills/`, rồi
   thêm mục vào `.claude-plugin/marketplace.json`.
2. Thêm skill = tạo thư mục + `SKILL.md` (copy `templates/SKILL_TEMPLATE.md`).
3. Ưu tiên skill **có script chạy được** khi có thể; nếu không, làm skill hướng
   dẫn/checklist rõ ràng.
4. Chạy `validate_skill.py` + `audit_skill.py` trước khi mở PR (xem
   `docs/security-model.md`).

## Ý tưởng bộ tương lai / future sets (chưa tạo)
- `mep-systems` — kiểm tra hệ thống MEP, size ống/ống gió, áp lực.
- `cost-qs` — bóc tách khối lượng, dự toán từ schedule.
- `gis-civil` — Civil 3D, surface, corridor, toạ độ khảo sát.
- Mở rộng `standards-qa` — BS 1192, COBie validation, layer standards.
