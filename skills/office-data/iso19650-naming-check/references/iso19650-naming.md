# ISO 19650 naming — tham chiếu / reference

Quy ước đặt tên **information container** theo ISO 19650 (kế thừa BS 1192 / UK
BIM Framework). Tên gồm các **trường** ngăn bằng dấu `-`, và **metadata**
suitability (status) + revision (thường ở CDE, đôi khi trong tên).

> ⚠️ Các danh mục dưới là **mặc định phổ biến**. Mỗi dự án/EIR/BEP có thể quy
> định khác — chỉnh qua `--rules my_rules.yaml`.

## Cấu trúc trường / field code
```
Project - Originator - Volume/System - Level/Location - Type - Role - Number
```
| Trường | Ý nghĩa | Mặc định |
|--------|---------|----------|
| Project | Mã dự án | 2–6 ký tự A–Z/0–9 |
| Originator | Đơn vị lập | 3–6 ký tự |
| Volume/System | Phân vùng chức năng | 1–2 ký tự (`ZZ`=toàn bộ) |
| Level/Location | Cao độ/vị trí | 2 ký tự (`XX`=N/A, `ZZ`=nhiều) |
| Type | Loại tài liệu | mã 2 ký tự (bảng dưới) |
| Role | Vai trò/bộ môn | 1 ký tự (bảng dưới) |
| Number | Số thứ tự | ≥4 chữ số |

## Mã Type (form) — thường gặp
`DR` bản vẽ 2D · `M3` mô hình 3D · `M2` mô hình 2D · `CM` mô hình phối hợp ·
`CR` clash rendition · `SP` specification · `SH` schedule · `RP` report ·
`SU` survey · `CA` calculations · `DB` database · `RI` RFI · `MI` minutes ·
`PR` programme · `SN` snagging · `ZZ` chung/khác.

## Mã Role (discipline)
`A` Architect · `B` Building surveyor · `C` Civil · `D` Drainage/Highways ·
`E` Electrical · `F` Facilities · `G` GIS/Land survey · `I` Interior ·
`K` Client · `L` Landscape · `M` Mechanical · `P` Public health ·
`Q` Quantity surveyor · `S` Structural · `T` Town planner · `W` Contractor ·
`X` Sub-contractor · `Y` Specialist designer · `Z` General.

## Suitability / status codes
- **WIP:** `S0`.
- **Shared:** `S1` (coordination), `S2` (information), `S3` (review & comment),
  `S4` (stage approval), `S6` (PIM authorization), `S7` (AIM authorization).
- **Published/Authorized:** `A1…An`, `B1…Bn`.
- **As constructed:** `CR`. (Bộ `D1…D4` tuỳ quy định.)

## Revision codes
- Mặc định pattern `^[PC][0-9]{2}(\.[0-9]{1,2})?$`.
- `P01, P02…` = preliminary; `C01, C02…` = construction/contractual.

## Rules tuỳ biến / custom rules (YAML)
```yaml
field_delimiter: "-"
fields:
  - {name: Project,    pattern: "^[A-Z0-9]{3}$"}
  - {name: Originator, pattern: "^[A-Z0-9]{3,6}$"}
  - {name: Volume,     pattern: "^[A-Z0-9]{1,2}$"}
  - {name: Location,   pattern: "^[A-Z0-9]{2}$"}
  - {name: Type,       allowed: [DR, M3, SP, SH, RP]}
  - {name: Role,       allowed: [A, S, M, E, P, C, Q]}
  - {name: Number,     pattern: "^[0-9]{4,}$"}
status_allowed: [S0, S1, S2, S3, S4, S6, S7, A1, A2, CR]
revision_pattern: "^[PC][0-9]{2}$"
```
