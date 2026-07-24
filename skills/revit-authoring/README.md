# Bộ skill Revit — `revit-authoring`

Bộ **Claude Skills** cho công việc Revit / Dynamo / pyRevit. Nhiều skill chạy
được **ngoài Revit** vì chúng đọc chính file Revit xuất ra (shared parameter
file, schedule CSV, warnings HTML); các skill còn lại giúp Claude **sinh script**
chạy trong Revit hoặc là **checklist hướng dẫn**.

## Skill trong bộ / skills in this set
| Skill | Loại | Làm gì |
|-------|------|--------|
| `dynamo-pyrevit-helper` | sinh script | Viết/rà soát script pyRevit & Dynamo (Transaction, collector, units) |
| `family-parameter-management` | ✅ chạy được | Phân tích shared parameter file: GUID/tên trùng, thiếu mô tả |
| `schedule-qa` | ✅ chạy được | Validate schedule CSV theo rules (required/unique/allowed) |
| `revit-warnings-audit` | ✅ chạy được | Gom nhóm & ưu tiên warning từ HTML export |
| `revit-model-audit` | hướng dẫn | Checklist sức khoẻ model (file size, purge, CAD, in-place…) |
| `revit-batch-export` | sinh script | Export hàng loạt sheet ra PDF/DWG/NWC/IFC theo tên chuẩn |

## Cài đặt / install (đây là Claude Skills)
Skill được Claude phát hiện qua file `SKILL.md`. Cài bằng một trong hai cách:

**1) Chép thủ công vào thư mục skills của bạn**
```bash
# Cài cho cá nhân (mọi dự án) — từng skill là một thư mục:
cp -r skills/revit-authoring/dynamo-pyrevit-helper       ~/.claude/skills/
cp -r skills/revit-authoring/family-parameter-management ~/.claude/skills/
cp -r skills/revit-authoring/schedule-qa                 ~/.claude/skills/
cp -r skills/revit-authoring/revit-warnings-audit        ~/.claude/skills/
cp -r skills/revit-authoring/revit-model-audit           ~/.claude/skills/
cp -r skills/revit-authoring/revit-batch-export          ~/.claude/skills/

# Hoặc cài cho riêng một dự án:
cp -r skills/revit-authoring/<skill> <project>/.claude/skills/
```
> Lưu ý: đặt **thư mục skill** (chứa `SKILL.md`) trực tiếp trong `~/.claude/skills/`,
> không lồng thêm cấp `revit-authoring/`.

**2) Nhờ Claude cài qua chat**
Mở repo này trong Claude Code và nói, ví dụ:
> "Cài bộ skill trong `skills/revit-authoring/` vào `~/.claude/skills/` cho tôi."

Sau khi cài, Claude tự chọn skill đúng theo `description` khi bạn nhắc tới việc
liên quan (vd "kiểm tra warning Revit", "so lỗi shared parameter").

## Dùng thử các skill chạy được / try the runnable ones
```bash
pip install -r ../../requirements.txt   # pyyaml (+ stdlib là đủ cho bộ này)

python family-parameter-management/scripts/analyze_shared_params.py \
       family-parameter-management/assets/sample_shared_params.txt

python schedule-qa/scripts/check_schedule.py \
       schedule-qa/assets/sample_schedule.csv --rules schedule-qa/assets/sample_rules.yaml

python revit-warnings-audit/scripts/parse_warnings.py \
       revit-warnings-audit/assets/sample_warnings.html
```

## Bảo mật / security
Như mọi skill trong repo, bộ này đã qua `validate_skill.py` + `audit_skill.py`
(không có finding HIGH). Xem `../../docs/security-model.md`.
