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

## Bốn bộ hiện có / four sets

### 1. `bim-coordination` — Coordination & Clash
| Skill | Trạng thái | Mô tả ngắn |
|-------|-----------|------------|
| `clash-report-analysis` | ✅ chạy được | Phân tích/tóm tắt report clash Navisworks (XML) |
| `shared-coordinates` | ✅ hướng dẫn | Thiết lập & QA toạ độ chung (SP/PBP/north) |
| `model-federation` | 🚧 scaffold | Gộp model coordination (NWF/NWD, ACC) |
| `coordination-issue-log` | 🚧 scaffold | Biến clash thành issue log giao việc |

### 2. `revit-authoring` — Revit / Dynamo / pyRevit
Bộ đầy đủ — xem [`skills/revit-authoring/README.md`](../skills/revit-authoring/README.md)
để biết cách cài đặt.

| Skill | Trạng thái | Mô tả ngắn |
|-------|-----------|------------|
| `dynamo-pyrevit-helper` | ✅ mẫu+ref | Viết/rà soát script pyRevit & Dynamo |
| `family-parameter-management` | ✅ chạy được | Phân tích shared parameter file (GUID/tên trùng, thiếu mô tả) |
| `schedule-qa` | ✅ chạy được | Validate schedule CSV theo rules (required/unique/allowed) |
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

## Mở rộng / how to grow
1. Thêm bộ mới = thư mục con của `skills/` (vd `mep-systems`, `cost-qs`, `gis-civil`).
2. Thêm skill = tạo thư mục + `SKILL.md` (copy `templates/SKILL_TEMPLATE.md`).
3. Ưu tiên skill **có script chạy được** khi có thể; nếu không, làm skill hướng
   dẫn/checklist rõ ràng.
4. Chạy `validate_skill.py` + `audit_skill.py` trước khi mở PR (xem
   `docs/security-model.md`).

## Ý tưởng bộ tương lai / future sets (chưa tạo)
- `mep-systems` — kiểm tra hệ thống MEP, size ống/ống gió, áp lực.
- `cost-qs` — bóc tách khối lượng, dự toán từ schedule.
- `gis-civil` — Civil 3D, surface, corridor, toạ độ khảo sát.
