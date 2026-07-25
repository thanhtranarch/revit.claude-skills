---
name: drawing-register-qa
description: Runs QA on a drawing issue register / transmittal before issue — flagging missing or badly-formatted revisions, invalid ISO 19650 suitability codes, missing issue dates, and duplicate sheet numbers from a CSV export. Use when checking a drawing register or transmittal for issue-readiness. Triggers on "drawing register", "issue sheet", "transmittal check", "revision check", "suitability code", "kiểm tra sổ phát hành", "revision bản vẽ".
license: MIT
---

# Drawing Register QA — Kiểm sổ phát hành bản vẽ

Soát drawing issue register / transmittal trước khi phát hành: bắt **revision
thiếu/sai định dạng**, **mã suitability không hợp lệ**, **thiếu ngày phát hành**,
và **số bản vẽ trùng**.
QA a drawing issue register: missing/bad revision, invalid suitability code,
missing issue date, and duplicate sheet numbers.

## Khi nào dùng / When to use
- Có drawing register / transmittal (CSV) chuẩn bị phát hành.
- Cần bảo đảm mọi bản vẽ có revision đúng, mã suitability hợp lệ, ngày phát hành.

## Cách dùng / How to use
```bash
python scripts/check_drawing_register.py <register.csv>
# tuỳ biến rule (revision pattern, danh mục suitability):
python scripts/check_drawing_register.py <register.csv> --rules my_rules.yaml
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/check_drawing_register.py assets/sample_drawing_register.csv
```

## Rule mặc định / default rules (`--rules` YAML để ghi đè)
- `revision_pattern`: `P01` / `C01` / `P01.1` / `A` / `1` (UK BIM revision).
- `status_allowed`: S0–S7, A1–A5, B1–B2, CR, D1–D2, WIP, Shared, Published…
- `require_revision`, `require_issue_date`: mặc định bật; `require_status`: tắt.

## Đầu ra / Output
- PASS/FAIL từng bản vẽ kèm lý do; tổng đạt / lỗi / số trùng. Exit 1 nếu có lỗi
  (dùng làm gate trước phát hành).

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `re`); `--rules` cần `pyyaml`.
- Bổ trợ `sheet-naming-check` (kiểm **pattern số/tên** sheet) — skill này kiểm
  **metadata phát hành** (revision/suitability/ngày). Dùng cả hai để soát toàn diện.
