# Revit shared parameter file — định dạng / format

File `.txt` tab-delimited xuất từ **Manage > Shared Parameters**. Không sửa tay
(dễ hỏng GUID). Cấu trúc theo section, mỗi dòng bắt đầu bằng một "tag".

```
# This is a Revit shared parameter file.
*META	VERSION	MINVERSION
META	2	1
*GROUP	ID	NAME
GROUP	1	Dimensions
*PARAM	GUID	NAME	DATATYPE	DATACATEGORY	GROUP	VISIBLE	DESCRIPTION	USERMODIFIABLE	HIDEWHENNOVALUE
PARAM	<guid>	Clear Width	LENGTH		1	1	Clear opening width	1	0
```

## Dòng GROUP
`GROUP <id> <name>` — định nghĩa nhóm parameter (map id ↔ tên).

## Dòng PARAM (cột theo thứ tự)
| Cột | Ý nghĩa |
|-----|---------|
| GUID | Định danh duy nhất — **không được trùng** |
| NAME | Tên hiển thị |
| DATATYPE | LENGTH, TEXT, INTEGER, NUMBER, YESNO, MATERIAL… |
| DATACATEGORY | (thường trống) |
| GROUP | id nhóm (khớp dòng GROUP) |
| VISIBLE | 1/0 hiển thị |
| DESCRIPTION | Mô tả (nên có) |
| USERMODIFIABLE | 1/0 người dùng sửa được |
| HIDEWHENNOVALUE | 1/0 |

## Vì sao GUID trùng nguy hiểm
Revit nhận diện shared parameter theo **GUID**, không theo tên. Hai dòng cùng
GUID = Revit coi là *một* parameter → tên/mô tả thứ hai bị bỏ qua, giá trị có
thể lẫn giữa các family. Đây là lỗi khó truy vết → script đánh dấu ngay.

## Ghi chú
- Data type có thể khác nhẹ theo phiên bản Revit; script chỉ đọc chuỗi thô nên
  không phụ thuộc danh mục cố định.
