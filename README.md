# t3lab-claude-skills

Bộ **skill cho Claude** dùng trong ngành ACE/AEC — coordination, clash, Revit,
so sánh markup PDF, tổng hợp comment, quản lý issue/RFI — kèm **lớp kiểm định
bảo mật** để duyệt skill do người khác đóng góp (chống mã độc & prompt-injection).

A Claude Code **plugin marketplace** for the AEC industry: 5 plugins (one per
domain) bundling Claude Skills, plus a **security vetting layer** to audit
community-contributed skills.

## Có gì / What's inside
```
skills/            5 nhóm phần mềm · 39 skill (xem docs/skill-taxonomy.md)
scripts/           validate_skill.py + audit_skill.py + build_taxonomy.py
.claude/agents/    skill-auditor — agent review bảo mật skill
.github/           CI (skill-validation), CODEOWNERS, PR template
docs/              skill-taxonomy.md, roadmap.md, security-model.md
templates/         SKILL_TEMPLATE.md
tests/fixtures/    malicious-skill — mẫu độc để test auditor
```

## Năm nhóm phần mềm / five software groups
Skill chia thư mục **theo phần mềm** (`skills/<software>/`), và gắn **metadata**
(`software`, `discipline`, `category`) để tra cứu chéo theo *bộ môn* và *tính chất*.

| Nhóm / group | Phần mềm | Skill |
|--------------|----------|-------|
| `revit` (20) | Revit / Dynamo / pyRevit | `rv-shared-parameters`, `rv-schedule-qa`, `rv-warnings-audit`, `rv-model-audit`, `rv-family-naming`, `rv-model-compare`, `rv-script-helper`, `rv-batch-export`, `rv-sheet-naming`, `rv-shared-coordinates`, `rv-comment-locations`, `rv-cad-import`, `rv-image-drafting`, `rv-create-sheets`, `rv-spellcheck-review`, `rv-create-family`, `rv-family-image`, `rvstr-beam-cad`, `rvstr-column-tools`, `rvmep-duct-velocity` |
| `navisworks` (2) | Navisworks | `clash-report-analysis`, `model-federation` |
| `acc-bim360` (2) | Autodesk Construction Cloud / BIM 360 | `acc-issue-register`, `coordination-issue-log` |
| `bluebeam-pdf` (2) | Bluebeam / PDF | `pdf-markup-compare`, `comment-aggregation` |
| `office-data` (13) | Excel / CSV (agnostic) | `rfi-tracker`, `risk-register`, `action-item-tracker`, `change-order-log`, `weekly-report`, `submittal-log`, `drawing-register-qa`, `iso19650-naming-check`, `iso19650-project-audit`, `cobie-validation`, `spellcheck-review`, `boq-compare`, `quantity-takeoff` |

> **Skill Revit đặt tên theo bộ môn** — `rv-` (chung/đa bộ môn), `rvarc-` (Kiến
> trúc), `rvstr-` (Kết cấu), `rvmep-` (MEP) — dạng `<prefix>-<a>-<b>` (đúng 2
> đoạn), enforce bởi `validate_skill.py`. Luật: [`CONTRIBUTING.md`](CONTRIBUTING.md).

**3 bảng tra cứu** (theo phần mềm / bộ môn / tính chất) sinh tự động:
[`docs/skill-taxonomy.md`](docs/skill-taxonomy.md) · lộ trình:
[`docs/roadmap.md`](docs/roadmap.md).

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
bằng `/<plugin>:<skill>` (vd `/revit-authoring:rv-schedule-qa`).

Thử/dev cục bộ không cần cài: `claude --plugin-dir ./plugins/revit-authoring`.

## Dùng nhanh (chạy script trực tiếp) / quick start
Nhiều skill kèm script chạy được ngay trên dữ liệu mẫu:
```bash
pip install -r requirements.txt

# Ví dụ: phân tích report clash Navisworks
python skills/navisworks/clash-report-analysis/scripts/parse_clash.py \
       skills/navisworks/clash-report-analysis/assets/sample_clash.xml

# So sánh markup 2 bản PDF
python skills/bluebeam-pdf/pdf-markup-compare/scripts/compare_markup.py \
       skills/bluebeam-pdf/pdf-markup-compare/assets/rev_a.pdf \
       skills/bluebeam-pdf/pdf-markup-compare/assets/rev_b.pdf

# Theo dõi RFI: aging, quá hạn, ball-in-court
python skills/office-data/rfi-tracker/scripts/track_rfis.py \
       skills/office-data/rfi-tracker/assets/sample_rfis.csv --as-of 2026-07-24

# So sánh 2 phiên bản model Revit (added/deleted/changed)
python skills/revit/rv-model-compare/scripts/compare_models.py \
       skills/revit/rv-model-compare/assets/sample_model_v1.csv \
       skills/revit/rv-model-compare/assets/sample_model_v2.csv
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
