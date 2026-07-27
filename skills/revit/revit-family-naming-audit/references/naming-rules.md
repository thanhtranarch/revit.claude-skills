# Family naming rules — reference & --rules template

Script `audit_family_names.py` dùng rule mặc định trong `DEFAULT_RULES`. Ghi đè
bằng file YAML qua `--rules`. Ví dụ:

```yaml
# my_rules.yaml — chỉ cần khai các key muốn đổi
name_pattern: "^[A-Z]{2,3}_[A-Za-z0-9]+(?:[_-][A-Za-z0-9]+)*$"
allowed_prefixes: [AR, ST, ME, EL, PL, FP, CI, LS, GN, FF, SP, SE]
prefix_delim: "_"
forbid_spaces: true
type_pattern: "^[A-Za-z0-9]+(?:[ _\\-x×]+[A-Za-z0-9]+)*$"
```

## Ý nghĩa các key / key meanings
| Key | Ý nghĩa |
|-----|---------|
| `name_pattern` | Regex tên family phải khớp. |
| `allowed_prefixes` | Danh mục prefix bộ môn hợp lệ (đoạn trước `prefix_delim`). |
| `prefix_delim` | Ký tự tách prefix khỏi phần còn lại (mặc định `_`). |
| `forbid_spaces` | `true` = cấm khoảng trắng trong tên family. |
| `type_pattern` | Regex tên type (chỉ áp khi chạy `--check-types`). |

## Prefix bộ môn gợi ý / suggested discipline prefixes
`AR` kiến trúc · `ST` kết cấu · `ME` cơ · `EL` điện · `PL` cấp thoát nước ·
`FP` PCCC · `CI` hạ tầng · `LS` cảnh quan · `GN` chung/generic · `FF` nội thất ·
`SP` chuyên dụng · `SE` an ninh. Chỉnh theo BEP/ tiêu chuẩn công ty.

## Cột đầu vào / input columns (alias)
- **Family**: Family, Family Name, FamilyName.
- **Type**: Type, Type Name, Family Type, Symbol.
- **Category**: Category, Cat, Revit Category.

Xuất danh sách này từ Revit bằng schedule "Family and Type", hoặc Dynamo/pyRevit
(duyệt `FilteredElementCollector` theo `FamilySymbol`).
