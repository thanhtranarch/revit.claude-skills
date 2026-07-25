# Drawing register QA — rules & columns

`check_drawing_register.py` dùng rule mặc định trong `DEFAULT_RULES`; ghi đè bằng
YAML qua `--rules`.

```yaml
# my_rules.yaml
revision_pattern: "^(P\\d{2}(\\.\\d{1,2})?|C\\d{2}(\\.\\d{1,2})?|[A-Z]|\\d{1,2})$"
status_allowed: [S0, S1, S2, S3, S4, S5, S6, S7, A1, A2, A3, B1, B2, CR, D1, D2]
require_revision: true
require_issue_date: true
require_status: false
```

## Ý nghĩa key / key meanings
| Key | Ý nghĩa |
|-----|---------|
| `revision_pattern` | Regex revision hợp lệ (vd `P01`, `C02`, `P01.1`, `A`, `1`). |
| `status_allowed` | Danh mục mã suitability được phép (so không phân biệt hoa/thường). |
| `require_revision` | `true` = bản vẽ phải có revision. |
| `require_issue_date` | `true` = phải có ngày phát hành. |
| `require_status` | `true` = phải có mã suitability (mặc định tắt). |

## Cột đầu vào / input columns (alias)
- **Sheet Number**: Sheet Number, Sheet No, Number, Drawing Number, Dwg No, No.
- **Sheet Name**: Sheet Name, Title, Drawing Title, Name, Description.
- **Revision**: Revision, Rev, Current Revision, Rev No.
- **Suitability**: Status, Suitability, Suitability Code, State, Purpose.
- **Issue Date**: Issue Date, Date, Issued, Date Issued, Revision Date.

## Suitability (ISO 19650 / UK BIM Framework)
`S0`–`S7` (WIP→shared), `A1`–`A5` (authorised/construction), `B1`–`B2`,
`CR`, `D1`–`D2`. Điều chỉnh danh mục theo EIR/BEP dự án.

## Liên quan / related
- `standards-qa/sheet-naming-check` — pattern số & tên sheet, từ cấm.
- `standards-qa/iso19650-naming-check` — tên **file** theo ISO 19650.
