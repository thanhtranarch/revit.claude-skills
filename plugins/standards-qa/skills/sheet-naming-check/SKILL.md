---
name: sheet-naming-check
description: Validate Revit/CAD sheet numbers, sheet names, and view names against a company naming standard (prefix/discipline/series/number pattern and allowed name vocabulary), reporting non-conforming and duplicate sheet numbers from an exported sheet list. Use when enforcing a titleblock/sheet-numbering standard or auditing a sheet list before issue. Triggers on "sheet naming", "sheet number standard", "view naming", "drawing register check", "chuẩn đặt tên sheet", "kiểm tra số bản vẽ".
status: scaffold
---

# Sheet Naming Check — Kiểm tra đặt tên sheet/view (SCAFFOLD)

> ⚠️ **Scaffold** — mới có khung. Expand before relying on it.

Kiểm tra sheet number / sheet name / view name theo chuẩn công ty (pattern
prefix-discipline-series-number + từ vựng tên cho phép), bắt sheet không đúng
chuẩn và **số bản vẽ trùng** từ sheet list export.

## Phạm vi dự kiến / planned scope
- Đầu vào: CSV export sheet list (Sheet Number, Sheet Name) từ Revit/CAD.
- Validate sheet number theo regex; bắt trùng số; kiểm tên theo từ vựng cho phép.
- Tái dùng khung của `iso19650-naming-check` và `revit-schedule-qa` (rules YAML).

## Việc cần làm / TODO
- [ ] Script validate sheet number pattern + duplicate + tên.
- [ ] Rules mẫu (discipline series, allowed name terms).

Liên quan / related: `iso19650-naming-check`, `revit-authoring/revit-schedule-qa`.
