# Revit — `skills/revit/`

Skill cho **Autodesk Revit** + **Dynamo / pyRevit**. Input thường là export từ
Revit (schedule CSV/TSV, warnings HTML, shared-parameter TXT, family/sheet list),
bản vẽ CAD (DXF) hoặc ảnh (PNG/JPEG), hoặc script chạy trong Revit.
Skills for Revit and Dynamo/pyRevit — model/data QA, standards, automation.

- **QA / kiểm tra:** `revit-model-audit`, `revit-warnings-audit`, `revit-model-compare`,
  `revit-schedule-qa`, `revit-duct-velocity-check` *(MEP)*
- **Tiêu chuẩn:** `revit-family-naming-audit`, `revit-family-parameter-management`,
  `revit-sheet-naming-check`, `revit-shared-coordinates`
- **Tự động hoá:** `revit-dynamo-pyrevit-helper`, `revit-batch-export`,
  `revit-model-from-cad`, `revit-image-to-drafting-view`, `revit-sheets-from-list`

Chi tiết + metadata + 3 bảng tra cứu: [`docs/skill-taxonomy.md`](../../docs/skill-taxonomy.md).
Lộ trình phát triển skill Revit: [`docs/roadmap.md`](../../docs/roadmap.md).
