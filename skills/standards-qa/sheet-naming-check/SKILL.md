---
name: sheet-naming-check
description: Validate Revit/CAD sheet numbers and sheet names against a company standard (discipline-prefix number pattern, allowed disciplines, forbidden placeholder terms) and report non-conforming and duplicate sheet numbers from an exported sheet list. Use when enforcing a titleblock/sheet-numbering standard or auditing a sheet list before issue. Triggers on "sheet naming", "sheet number standard", "drawing register check", "duplicate sheet number", "chuẩn đặt tên sheet", "kiểm tra số bản vẽ".
---

# Sheet Naming Check — Kiểm tra số & tên sheet

Kiểm sheet number / sheet name theo chuẩn công ty: số sheet theo **pattern +
prefix bộ môn cho phép**, bắt **số trùng**, tên rỗng và **từ cấm** trong tên
(Copy/Draft/DO NOT USE...) — từ sheet list export của Revit/CAD.
Validate sheet numbers/names against a company standard, flagging non-conforming
and duplicate sheet numbers.

## Khi nào dùng / When to use
- Có sheet list export (Revit: Sheet List schedule → CSV; hoặc CAD register).
- Cần soát bản vẽ trước phát hành: đúng chuẩn số, không trùng, tên hợp lệ.

## Cách dùng / How to use
```bash
python scripts/check_sheet_naming.py <sheets.csv>
# tuỳ biến rule (pattern, discipline, từ cấm):
python scripts/check_sheet_naming.py <sheets.csv> --rules my_rules.yaml
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/check_sheet_naming.py assets/sample_sheets.csv
```

## Rule mặc định / default rules (ghi đè bằng `--rules` YAML)
- `number_pattern`: `^[A-Z]{1,2}[-.]?\d{2,4}[A-Z]?$` — vd `A-101`, `S201`, `M-301A`.
- `allowed_disciplines`: A, S, M, E, P, C, L, FP, T, G, ID.
- `forbidden_name_terms`: copy, draft, do not use, test, temp, xxx, tbc.
- `require_name`: bắt buộc có tên sheet.

## Đầu ra / Output
- PASS/FAIL từng sheet kèm lý do (sai pattern, prefix lạ, tên rỗng, từ cấm, **trùng số**).
- Tổng: đạt, lỗi, số sheet trùng. Exit 1 nếu có lỗi (dùng làm gate trước phát hành).

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `re`); `--rules` cần `pyyaml`.
- Tự dò cột Sheet Number / Sheet Name theo alias.
- Bổ trợ `iso19650-naming-check` (tên file) & `spellcheck-review` (chính tả tên sheet).
