# Sheet naming rules — reference & --rules template

`check_sheet_naming.py` dùng rule mặc định trong `DEFAULT_RULES`; ghi đè bằng YAML
qua `--rules`. Chỉ cần khai các key muốn đổi:

```yaml
# my_rules.yaml
number_pattern: "^[A-Z]{1,2}[-.]?\\d{2,4}[A-Z]?$"
allowed_disciplines: [A, S, M, E, P, C, L, FP, T, G, ID]
forbidden_name_terms: [copy, draft, "do not use", test, temp, xxx, tbc]
require_name: true
```

## Ý nghĩa key / key meanings
| Key | Ý nghĩa |
|-----|---------|
| `number_pattern` | Regex số sheet phải khớp (so khớp sau khi viết hoa). |
| `allowed_disciplines` | Prefix bộ môn hợp lệ (các chữ cái đầu của số sheet). |
| `forbidden_name_terms` | Từ không được xuất hiện trong tên sheet (placeholder/nháp). |
| `require_name` | `true` = tên sheet không được rỗng. |

## Prefix bộ môn phổ biến / common discipline prefixes
`A` kiến trúc · `S` kết cấu · `M` cơ (HVAC) · `E` điện · `P` cấp thoát nước ·
`C` hạ tầng/civil · `L` cảnh quan · `FP` PCCC · `T` viễn thông · `G` chung ·
`ID` nội thất. Chỉnh theo tiêu chuẩn/BEP dự án.

## Cột đầu vào / input columns (alias)
- **Sheet Number**: Sheet Number, Sheet No, Number, No, Sheet, Drawing Number, Dwg No.
- **Sheet Name**: Sheet Name, Name, Title, Sheet Title, Drawing Title, Description.

Xuất từ Revit: **View > Schedules > Sheet List** (thêm cột Sheet Number, Sheet
Name) → Export CSV.

## Lỗi thường gặp / common failures
- Số trùng do copy sheet mà chưa đổi số.
- Prefix sai bộ môn (vd dùng `X` không có trong danh mục).
- Tên còn "Copy of…", "DRAFT", "DO NOT USE", để trống.
- Số không theo pattern (thiếu prefix, sai số chữ số).
