# Rules file reference — schedule-qa

Rules là file YAML mô tả ràng buộc cho một schedule đã export ra CSV/TSV.

## Khoá hỗ trợ / supported keys
| Khoá | Kiểu | Ý nghĩa |
|------|------|---------|
| `delimiter` | chuỗi | Ký tự phân tách (`,` mặc định; `"\t"` cho tab-delimited) |
| `required` | list cột | Các cột **không được để trống** ở mọi dòng |
| `unique` | list cột | Các cột giá trị phải **duy nhất** (vd Mark) |
| `allowed` | map cột→list | Danh sách **giá trị hợp lệ** cho từng cột |

## Ví dụ / example
```yaml
delimiter: ","
required: [Mark, Fire Rating]
unique:   [Mark]
allowed:
  Fire Rating: ["1 HR", "2 HR", "None"]
  Level:       ["Level 1", "Level 2", "Level 3", "Roof"]
```

## Loại vi phạm báo ra / violation types
- `BLANK REQUIRED` — ô bắt buộc để trống.
- `NOT ALLOWED` — giá trị không nằm trong `allowed`.
- `DUPLICATE` — trùng ở cột `unique` (kèm dòng bị trùng).
- `MISSING COLUMN` — cột nêu trong rules không có trong file export.

## Mẹo / tips
- Export schedule giữ nguyên tên cột như trong Revit; rules phải khớp tên cột.
- Ô trống của giá trị `allowed` được bỏ qua (dùng `required` nếu muốn bắt trống).
- Có thể tạo nhiều rules file cho từng loại schedule (door/room/equipment…).
