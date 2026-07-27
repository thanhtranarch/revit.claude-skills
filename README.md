# t3lab-claude-skills

Bộ **skill cho Claude** dùng trong ngành ACE/AEC — coordination, clash, Revit,
so sánh markup PDF, tổng hợp comment, quản lý issue/RFI — kèm **lớp kiểm định
bảo mật** để duyệt skill do người khác đóng góp (chống mã độc & prompt-injection).

A Claude Code **plugin marketplace** for the AEC industry: 5 plugins (one per
domain) bundling Claude Skills, plus a **security vetting layer** to audit
community-contributed skills.

## Có gì / What's inside
```
.claude-plugin/marketplace.json   catalog liệt kê 5 plugin
plugins/<bộ>/                     mỗi bộ = 1 plugin (.claude-plugin/plugin.json + skills/)
scripts/                          validate_skill.py, audit_skill.py, validate_marketplace.py
.claude/agents/                   skill-auditor — agent review bảo mật skill (dev-tooling)
.github/                          CI (skill-validation), CODEOWNERS, PR template
docs/                             skill-taxonomy.md, security-model.md
templates/                        SKILL_TEMPLATE.md
tests/fixtures/                   malicious-skill — mẫu độc để test auditor
```

## Năm plugin / five plugins
| Plugin | Nội dung | Skill chạy được |
|--------|----------|-----------------|
| `bim-coordination` | Clash & coordination | `clash-report-analysis`, `shared-coordinates` |
| `revit-authoring` | Revit / Dynamo / pyRevit | `revit-family-parameter-management`, `revit-schedule-qa`, `revit-warnings-audit`, `revit-dynamo-pyrevit-helper`, `revit-batch-export` |
| `documentation-review` | Markup & comment | `pdf-markup-compare`, `comment-aggregation` |
| `project-management` | ACC/BIM360 & Excel | `acc-issue-register` |
| `standards-qa` | Chuẩn & QA tài liệu | `iso19650-naming-check`, `spellcheck-review` |

Bản đồ đầy đủ + skill scaffold: [`docs/skill-taxonomy.md`](docs/skill-taxonomy.md).

## Cài đặt / install (Claude Code plugin)
Thêm marketplace một lần, rồi cài từng plugin bạn cần:
```
/plugin marketplace add thanhtranarch/t3lab-claude-skills
/plugin install revit-authoring@t3lab-ace-skills
/plugin install standards-qa@t3lab-ace-skills
/reload-plugins
```
Hoặc nhờ Claude qua chat: *"Thêm marketplace t3lab-claude-skills rồi cài plugin
revit-authoring."* Sau khi cài, Claude tự chọn skill theo `description`; gọi tay
bằng `/<plugin>:<skill>` (vd `/revit-authoring:revit-schedule-qa`).

Thử/dev cục bộ không cần cài: `claude --plugin-dir ./plugins/revit-authoring`.

## Dùng nhanh (chạy script trực tiếp) / quick start
Nhiều skill kèm script chạy được ngay trên dữ liệu mẫu:
```bash
pip install -r requirements.txt

python plugins/bim-coordination/skills/clash-report-analysis/scripts/parse_clash.py \
       plugins/bim-coordination/skills/clash-report-analysis/assets/sample_clash.xml

python plugins/documentation-review/skills/pdf-markup-compare/scripts/compare_markup.py \
       plugins/documentation-review/skills/pdf-markup-compare/assets/rev_a.pdf \
       plugins/documentation-review/skills/pdf-markup-compare/assets/rev_b.pdf
```

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
# Kiểm định manifest + toàn bộ skill:
python scripts/validate_marketplace.py
python scripts/validate_skill.py plugins
python scripts/audit_skill.py    plugins

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
