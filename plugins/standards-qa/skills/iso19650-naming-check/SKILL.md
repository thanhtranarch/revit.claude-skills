---
name: iso19650-naming-check
description: Validate information-container (file) names against the ISO 19650 / UK BIM Framework naming convention — the field-based code Project-Originator-Volume-Location-Type-Role-Number, plus optional suitability/status (S0, S2, A1…) and revision (P01, C01…) codes. Checks field count, field patterns, and known Type/Role code sets, reporting each bad name with the exact field that failed. Use when auditing a file register, a CDE export, or a drawing list for ISO 19650 naming compliance. Triggers on "ISO 19650", "19650 naming", "file naming standard", "BS 1192", "container naming", "CDE naming check", "kiểm tra đặt tên file", "chuẩn đặt tên ISO 19650".
---

# ISO 19650 Naming Check — Kiểm tra đặt tên file theo ISO 19650

Kiểm tra tên information container (file) theo quy ước ISO 19650 / UK BIM
Framework: mã theo trường `Project-Originator-Volume-Location-Type-Role-Number`,
kèm (tuỳ chọn) mã **suitability/status** (S0, S2, A1…) và **revision** (P01, C01…).
Validate file names against the ISO 19650 field-based naming convention.

## Khi nào dùng / When to use
- Audit một file register / export CDE / drawing list xem có đúng chuẩn đặt tên.
- Bắt tên sai trường, thiếu trường, sai mã Type/Role, sai status/revision.

## Cách dùng / How to use
```bash
# Từ CSV (tự dò cột tên file; có thể chỉ định cột status/revision):
python scripts/check_iso19650.py <register.csv>
python scripts/check_iso19650.py <register.csv> --name-col "File Name" \
       --status-col Suitability --rev-col Revision

# Từ danh sách tên file (mỗi dòng 1 tên .txt):
python scripts/check_iso19650.py <filenames.txt>

# Dùng bộ quy tắc tuỳ biến (mã Type/Role, độ dài trường… theo dự án):
python scripts/check_iso19650.py <register.csv> --rules my_rules.yaml
```
Thử nhanh với mẫu / quick test:
```bash
python scripts/check_iso19650.py assets/sample_filenames.csv
```

## Cấu trúc mã / the field code (mặc định 7 trường)
```
Project - Originator - Volume/System - Level/Location - Type - Role - Number
  PRJ   -    ABC     -      XX        -      00        -  DR  -  A   - 0001
```
+ tuỳ chọn `Status` (S0/S1/S2/S3/S4/S6/S7, A1…, B1…, CR) và `Revision`
(`P01`, `C02`…). Xem danh mục mã Type/Role trong `references/iso19650-naming.md`.

## Đầu ra / Output
- Mỗi tên: PASS hoặc FAIL kèm **trường sai** và lý do.
- Tóm tắt: tổng, số đạt, số lỗi. Exit ≠ 0 nếu có lỗi (dùng được trong QA/CI).

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (regex + csv); `--rules` cần `pyyaml` (đã có trong
  requirements). Mã Type/Role và độ dài trường **tuỳ biến được** — mỗi dự án/
  EIR có thể khác; chỉnh trong rules YAML.
