# t3lab-claude-skills

Bộ **skill cho Claude** dùng trong ngành ACE/AEC — coordination, clash, Revit,
so sánh markup PDF, tổng hợp comment, quản lý issue/RFI — kèm **lớp kiểm định
bảo mật** để duyệt skill do người khác đóng góp (chống mã độc & prompt-injection).

A library of **Claude Skills** for the AEC industry, plus a **security vetting
layer** to audit community-contributed skills.

## Có gì / What's inside
```
skills/            4 bộ skill (xem docs/skill-taxonomy.md)
scripts/           validate_skill.py + audit_skill.py — lớp kiểm định
.claude/agents/    skill-auditor — agent review bảo mật skill
.github/           CI (skill-validation), CODEOWNERS, PR template
docs/              skill-taxonomy.md, security-model.md
templates/         SKILL_TEMPLATE.md
tests/fixtures/    malicious-skill — mẫu độc để test auditor
```

## Bốn bộ skill / four skill sets
| Bộ | Nội dung | Skill chạy được |
|----|----------|-----------------|
| `bim-coordination` | Clash & coordination | `clash-report-analysis`, `shared-coordinates` |
| `revit-authoring` | Revit / Dynamo / pyRevit | `family-parameter-management`, `schedule-qa`, `revit-warnings-audit`, `dynamo-pyrevit-helper`, `revit-batch-export` |
| `documentation-review` | Markup & comment | `pdf-markup-compare`, `comment-aggregation` |
| `project-management` | ACC/BIM360 & Excel | `acc-issue-register` |

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
