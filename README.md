# t3lab-claude-skills

Bộ **skill cho Claude** dùng trong ngành ACE/AEC — coordination, clash, Revit,
so sánh markup PDF, tổng hợp comment, quản lý issue/RFI — kèm **lớp kiểm định
bảo mật** để duyệt skill do người khác đóng góp (chống mã độc & prompt-injection).

A library of **Claude Skills** for the AEC industry, plus a **security vetting
layer** to audit community-contributed skills.

## Có gì / What's inside
```
skills/            7 bộ skill · 29 skill (xem docs/skill-taxonomy.md)
scripts/           validate_skill.py + audit_skill.py — lớp kiểm định
.claude/agents/    skill-auditor — agent review bảo mật skill
.github/           CI (skill-validation), CODEOWNERS, PR template
docs/              skill-taxonomy.md, security-model.md
templates/         SKILL_TEMPLATE.md
tests/fixtures/    malicious-skill — mẫu độc để test auditor
```

## Bảy bộ skill / seven skill sets
| Bộ | Nội dung | Skill chạy được / runnable |
|----|----------|---------------------------|
| `bim-coordination` | Clash & coordination | `clash-report-analysis`, `coordination-issue-log`, `model-federation`, `shared-coordinates` |
| `revit-authoring` | Revit / Dynamo / pyRevit | `family-parameter-management`, `schedule-qa`, `revit-warnings-audit`, `revit-model-audit`, `family-naming-audit`, `model-compare`, `dynamo-pyrevit-helper`, `revit-batch-export` |
| `documentation-review` | Markup & comment | `pdf-markup-compare`, `comment-aggregation`, `submittal-log`, `drawing-register-qa` |
| `project-management` | ACC/BIM360 & Excel | `acc-issue-register`, `rfi-tracker`, `weekly-report`, `change-order-log`, `action-item-tracker`, `risk-register` |
| `standards-qa` | Chuẩn & QA tài liệu | `iso19650-naming-check`, `spellcheck-review`, `sheet-naming-check`, `cobie-validation` |
| `cost-qs` | Bóc tách khối lượng & chi phí | `quantity-takeoff`, `boq-compare` |
| `mep-systems` | Kiểm tra hệ thống MEP | `duct-velocity-check` |

Bản đồ đầy đủ + skill scaffold: [`docs/skill-taxonomy.md`](docs/skill-taxonomy.md).

## Dùng nhanh / quick start
```bash
pip install -r requirements.txt

# Ví dụ: phân tích report clash Navisworks
python skills/bim-coordination/clash-report-analysis/scripts/parse_clash.py \
       skills/bim-coordination/clash-report-analysis/assets/sample_clash.xml

# So sánh markup 2 bản PDF
python skills/documentation-review/pdf-markup-compare/scripts/compare_markup.py \
       skills/documentation-review/pdf-markup-compare/assets/rev_a.pdf \
       skills/documentation-review/pdf-markup-compare/assets/rev_b.pdf

# Theo dõi RFI: aging, quá hạn, ball-in-court
python skills/project-management/rfi-tracker/scripts/track_rfis.py \
       skills/project-management/rfi-tracker/assets/sample_rfis.csv --as-of 2026-07-24

# So sánh 2 phiên bản model Revit (added/deleted/changed)
python skills/revit-authoring/model-compare/scripts/compare_models.py \
       skills/revit-authoring/model-compare/assets/sample_model_v1.csv \
       skills/revit-authoring/model-compare/assets/sample_model_v2.csv
```

### Dùng như Claude Skills
Trong Claude Code, các skill trong `skills/` được Claude tự chọn theo
`description`. Bạn cũng có thể chép một bộ vào `~/.claude/skills/` hoặc
`.claude/skills/` của dự án khác để tái sử dụng.

## Bảo mật / security (điểm nhấn)
Vì repo nhận skill từ nhiều người, mọi skill được kiểm định nhiều tầng trước
khi merge — xem [`docs/security-model.md`](docs/security-model.md):

1. `scripts/validate_skill.py` — cấu trúc & metadata SKILL.md.
2. `scripts/audit_skill.py` — quét tĩnh mã độc / lệnh nguy hiểm / rò rỉ dữ liệu /
   prompt-injection (regex + AST, chỉ stdlib + pyyaml).
3. Agent `@skill-auditor` — review có ngữ cảnh, verdict PASS/FAIL.
4. CI `.github/workflows/skill-validation.yml` — chạy tầng 1–2 trên mọi PR.
5. `CODEOWNERS` — maintainer duyệt lần cuối.

```bash
# Kiểm định toàn bộ skill:
python scripts/validate_skill.py skills
python scripts/audit_skill.py    skills

# Chứng minh auditor bắt được mã độc:
python scripts/audit_skill.py tests/fixtures/malicious-skill   # exit != 0
```

## Đóng góp / contributing
Xem [`CONTRIBUTING.md`](CONTRIBUTING.md). Tóm tắt: copy `templates/SKILL_TEMPLATE.md`,
viết skill, chạy validate + audit, mở PR (CI + review sẽ kiểm định).

## Yêu cầu / requirements
Python 3.11+. Cài deps: `pip install -r requirements.txt`. Lớp kiểm định chỉ
cần `pyyaml` + thư viện chuẩn.

## License
Phát hành theo giấy phép **MIT** — xem [`LICENSE`](LICENSE). Bạn được tự do
dùng, sửa và chia sẻ; giữ lại dòng bản quyền & giấy phép.
Released under the **MIT License** — see [`LICENSE`](LICENSE).
