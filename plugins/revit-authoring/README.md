# Plugin: `revit-authoring`

Bộ **Claude Skills** cho công việc Revit / Dynamo / pyRevit. Nhiều skill chạy
được **ngoài Revit** vì chúng đọc chính file Revit xuất ra (shared parameter
file, schedule CSV, warnings HTML); các skill còn lại giúp Claude **sinh script**
chạy trong Revit hoặc là **checklist hướng dẫn**.

## Skills
| Skill (gọi `/revit-authoring:<skill>`) | Loại | Làm gì |
|-------|------|--------|
| `revit-family-parameter-management` | ✅ chạy được | Phân tích shared parameter file: GUID/tên trùng, thiếu mô tả |
| `revit-schedule-qa` | ✅ chạy được | Validate schedule CSV theo rules (required/unique/allowed) |
| `revit-warnings-audit` | ✅ chạy được | Gom nhóm & ưu tiên warning từ HTML export |
| `revit-model-audit` | hướng dẫn | Checklist sức khoẻ model (file size, purge, CAD, in-place…) |
| `revit-batch-export` | sinh script | Export hàng loạt sheet ra PDF/DWG/NWC/IFC theo tên chuẩn |
| `revit-dynamo-pyrevit-helper` | sinh script | Viết/rà soát script pyRevit & Dynamo (Transaction, collector, units) |

## Cài đặt / install
```
/plugin marketplace add thanhtranarch/t3lab-claude-skills
/plugin install revit-authoring@t3lab-ace-skills
/reload-plugins
```
Hoặc nhờ Claude qua chat: *"Thêm marketplace t3lab-claude-skills và cài plugin
revit-authoring."* Sau khi cài, Claude tự chọn skill theo `description`; gọi tay
bằng `/revit-authoring:<skill>`.

## Python deps
```bash
pip install pyyaml   # cho revit-schedule-qa; các skill khác dùng thư viện chuẩn
```

## Dùng thử các skill chạy được / try the runnable ones
```bash
python skills/revit-family-parameter-management/scripts/analyze_shared_params.py \
       skills/revit-family-parameter-management/assets/sample_shared_params.txt

python skills/revit-schedule-qa/scripts/check_schedule.py \
       skills/revit-schedule-qa/assets/sample_schedule.csv --rules skills/revit-schedule-qa/assets/sample_rules.yaml

python skills/revit-warnings-audit/scripts/parse_warnings.py \
       skills/revit-warnings-audit/assets/sample_warnings.html
```

## Bảo mật / security
Bộ này đã qua `validate_skill.py` + `audit_skill.py` ở gốc repo (không có finding
HIGH). Xem `../../docs/security-model.md`.
