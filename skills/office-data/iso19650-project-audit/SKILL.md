---
name: iso19650-project-audit
description: Audits a whole ISO 19650 CDE / container register (CSV) for project-level information-management conformance — metadata completeness, valid suitability and revision codes, ISO 8601 dates, and consistency between CDE state and suitability/revision — then scores overall conformance and can check delivered containers against an expected MIDP list. Use when checking whether a project's information containers meet the ISO 19650 / BIM standard beyond just file naming, before a stage gate or handover. Triggers on "ISO 19650 audit", "BIM standard compliance", "CDE register check", "suitability code", "MIDP check", "project ISO 19650", "kiểm tra ISO 19650 dự án", "tuân thủ BIM", "kiểm tra CDE".
license: MIT
metadata:
  software: office-data
  discipline: multi
  category: standards
---

# ISO 19650 Project Audit — Kiểm tra tuân thủ ISO 19650 cả dự án

Soát **mức độ tuân thủ ISO 19650 của cả dự án** từ một CDE/container register
(CSV): metadata đầy đủ, mã suitability/revision hợp lệ, ngày ISO 8601, và **tính
nhất quán giữa trạng thái CDE ↔ suitability ↔ revision** — rồi **chấm điểm** tuân
thủ và (tuỳ chọn) đối chiếu với danh sách container kỳ vọng (MIDP).
Project-level ISO 19650 conformance audit over a CDE register, with a scorecard.

## Khi nào dùng / When to use
- Cần biết **dự án đã khớp chuẩn BIM/ISO 19650 chưa** — không chỉ đặt tên file.
- Trước **mốc phát hành / stage gate / bàn giao**: kiểm CDE register đã sạch chưa.
- Muốn **scorecard** % tuân thủ theo từng hạng mục + danh sách container chưa đạt.

## Khác gì `iso19650-naming-check` / how it differs
- `iso19650-naming-check` → chỉ soát **tên file** (field structure, Type/Role…).
- Skill này → soát **thông tin quản lý cấp dự án**: metadata, suitability/revision,
  nhất quán trạng thái CDE, và độ phủ MIDP. Dùng kèm nhau.

## Cách dùng / How to use
```bash
# Audit + scorecard:
python scripts/audit_iso19650_project.py <register.csv>

# Đối chiếu danh sách kỳ vọng (MIDP) + xuất findings CSV:
python scripts/audit_iso19650_project.py <register.csv> \
       --expected midp.csv --csv out/findings.csv

# Tuỳ biến mã theo BEP dự án + JSON:
python scripts/audit_iso19650_project.py <register.csv> --rules bep_rules.yaml --json
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/audit_iso19650_project.py assets/sample_cde_register.csv
```
Cột tự dò (name/title/originator/suitability/revision/state/date); ép bằng
`--name-col`, `--suitability-col`, `--state-col`… nếu header lạ.

## Đầu ra / Output
- **Scorecard**: tổng container, số **đạt hoàn toàn**, % tuân thủ; điểm theo 6 hạng
  mục (metadata, tên, suitability, revision, date, nhất quán trạng thái).
- Rollup theo **trạng thái CDE** và **suitability**.
- Danh sách **container chưa đạt** kèm lý do; (tuỳ chọn) container **thiếu so với
  MIDP**.
- Exit 0 nếu ≥ `--threshold` (mặc định 100%) và không thiếu MIDP; ngược lại 1.

## Tài nguyên / Resources
- `scripts/audit_iso19650_project.py` — bộ kiểm (chỉ stdlib; `--rules` cần pyyaml).
- `references/iso19650-checklist.md` — bảng mã CDE state / suitability / revision +
  ranh giới *tự động kiểm* vs *cần người review*.
- `assets/sample_cde_register.csv` — register mẫu (đạt & chưa đạt) để test.

## Ghi chú / Notes
- Mã mặc định theo **UK BIM Framework**; **luôn ưu tiên BEP/EIR dự án** — tuỳ biến
  qua `--rules` (suitability_allowed, revision_pattern, required_fields…).
- Chỉ kiểm được **metadata**, không kiểm chất lượng *nội dung* model; LOIN/LOD,
  TIDP/MIDP đầy đủ vẫn cần người review (xem checklist).
