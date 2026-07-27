---
name: rv-family-naming
description: Audits Revit family and type names from an exported family list against a company naming standard — discipline prefix, allowed pattern, no spaces or double underscores — and flags names reused across categories and duplicate (family, type) pairs. Use when enforcing a family naming convention or cleaning up a library before issue. Triggers on "family naming", "family name standard", "family library audit", "type naming", "chuẩn tên family", "kiểm tra tên family".
license: MIT
metadata:
  software: revit
  discipline: multi
  category: standards
---

# Family Naming Audit — Kiểm tra tên family/type Revit

Kiểm tra tên family & type từ file export (Family, Type, Category) theo chuẩn
công ty: prefix bộ môn, pattern cho phép, không khoảng trắng / gạch dưới đôi;
bắt tên **dùng lại qua nhiều category** và cặp **(Family, Type) trùng lặp**.
Audit family/type names against a naming standard, flagging cross-category reuse
and duplicate pairs.

## Khi nào dùng / When to use
- Có danh sách family export (Dynamo/pyRevit/schedule) dạng CSV.
- Cần chuẩn hoá thư viện family trước khi phát hành hoặc gộp vào template công ty.

## Cách dùng / How to use
```bash
python scripts/audit_family_names.py <families.csv>
# tuỳ biến rule (prefix, pattern) + kiểm cả tên type:
python scripts/audit_family_names.py <families.csv> --rules my_rules.yaml --check-types
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/audit_family_names.py assets/sample_families.csv
```

## Rule mặc định / default rules (ghi đè bằng `--rules` YAML)
- `name_pattern`: `^[A-Z]{2,3}_<đoạn>(_<đoạn>)*$` — prefix bộ môn + các đoạn.
- `allowed_prefixes`: AR, ST, ME, EL, PL, FP, CI, LS, GN, FF, SP, SE.
- Cấm khoảng trắng, gạch dưới đôi `__`, gạch dưới đầu/cuối.
- `type_pattern` (khi `--check-types`): cho phép chữ/số + `x × _ -` (vd `600x900`).

## Đầu ra / Output
- PASS/FAIL từng family kèm lý do; danh sách type sai pattern (nếu `--check-types`).
- Danh sách **(Family, Type) trùng lặp** và **tên dùng lại qua nhiều category**.
- Tổng: số family riêng biệt, đạt, lỗi, cặp trùng. Exit 1 nếu có lỗi (gate được).

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `re`); `--rules` cần `pyyaml`.
- Tự dò cột Family/Type/Category theo alias; thiếu Type/Category vẫn chạy.
