# Revit — `skills/revit/`

Skill cho **Autodesk Revit** + **Dynamo / pyRevit**. Input thường là export từ
Revit (schedule CSV/TSV, warnings HTML, shared-parameter TXT, family/sheet list),
bản vẽ CAD (DXF) hoặc ảnh (PNG/JPEG), script chạy trong Revit, hoặc thao tác model
qua **Revit MCP / pyRevit / Dynamo**.
Skills for Revit and Dynamo/pyRevit — model/data QA, standards, automation.

## Đặt tên theo bộ môn / discipline prefixes
Skill Revit đặt tên `<prefix>-<đoạn1>-<đoạn2>` (prefix bộ môn + **đúng 2 đoạn**),
với `metadata.discipline` khớp prefix — enforce tự động bởi
`scripts/validate_skill.py`:

| Prefix | Bộ môn | `discipline` |
|--------|--------|--------------|
| `rv-`    | Revit chung / đa bộ môn (general) | `multi` |
| `rvarc-` | Kiến trúc / Architecture          | `architecture` |
| `rvstr-` | Kết cấu / Structural              | `structural` |
| `rvmep-` | MEP                               | `mep` |

Luật đầy đủ: [`CONTRIBUTING.md`](../../CONTRIBUTING.md) → *Quy ước đặt tên skill Revit*.

## Skill hiện có / current skills

**`rv-` — chung / general (đa bộ môn)**
- *QA / kiểm tra:* `rv-model-audit`, `rv-warnings-audit`, `rv-model-compare`, `rv-schedule-qa`
- *Tiêu chuẩn:* `rv-family-naming`, `rv-shared-parameters`, `rv-sheet-naming`, `rv-spellcheck-review`
- *Điều phối:* `rv-comment-locations`, `rv-shared-coordinates`
- *Tự động hoá:* `rv-script-helper`, `rv-batch-export`, `rv-cad-import`, `rv-image-drafting`, `rv-create-sheets`, `rv-create-family`, `rv-family-image` *(MCP)*

**`rvstr-` — Kết cấu / Structural**
- `rvstr-beam-cad` — tạo Structural Beam từ layer CAD đã import *(MCP)*
- `rvstr-column-tools` — cột: replace wall→column, extract toạ độ, dim-to-grid *(MCP)*

**`rvmep-` — MEP**
- `rvmep-duct-velocity` — kiểm vận tốc gió & aspect ratio từ duct schedule

**`rvarc-` — Kiến trúc / Architecture** — *chưa có; để dành cho skill đặc thù Kiến trúc.*

Chi tiết + metadata + 3 bảng tra cứu: [`docs/skill-taxonomy.md`](../../docs/skill-taxonomy.md).
Lộ trình phát triển skill Revit: [`docs/roadmap.md`](../../docs/roadmap.md).
