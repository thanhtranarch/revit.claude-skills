# Revit — `skills/revit/`

Skill cho **Autodesk Revit** + **Dynamo / pyRevit**. Input thường là export từ
Revit (schedule CSV/TSV, warnings HTML, shared-parameter TXT, family/sheet list),
bản vẽ CAD (DXF) hoặc ảnh (PNG/JPEG), hoặc script chạy trong Revit.
Skills for Revit and Dynamo/pyRevit — model/data QA, standards, automation.

- **QA / kiểm tra:** `revit-model-audit`, `revit-warnings-audit`, `revit-model-compare`,
  `revit-schedule-qa`, `revit-duct-velocity` *(MEP)*
- **Tiêu chuẩn:** `revit-family-naming`, `revit-shared-parameters`,
  `revit-sheet-naming`, `revit-shared-coordinates`, `revit-spellcheck-review`
- **Tự động hoá:** `revit-script-helper`, `revit-batch-export`,
  `revit-cad-import`, `revit-image-drafting`, `revit-create-sheets`,
  `revit-create-family`

Chi tiết + metadata + 3 bảng tra cứu: [`docs/skill-taxonomy.md`](../../docs/skill-taxonomy.md).
Lộ trình phát triển skill Revit: [`docs/roadmap.md`](../../docs/roadmap.md).
