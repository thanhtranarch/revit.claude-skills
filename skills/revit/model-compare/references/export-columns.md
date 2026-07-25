# Model export columns — chuẩn bị dữ liệu so sánh

`compare_models.py` ghép hai file theo **một cột ID ổn định**. Để so sánh có
nghĩa, cùng element phải giữ nguyên ID giữa hai phiên bản.

## Cột ID / id column (alias tự dò)
`Element ID`, `ElementId`, `Id`, `GUID`, `Unique ID`, `UniqueId`, `IFC GUID`.

- **Element ID** (số) đổi khi element bị xoá-tạo lại ⇒ dễ báo "added+deleted" thay
  vì "changed". Ổn định hơn: **UniqueId** (GUID) — không đổi qua các lần lưu.
- Nếu không dò được cột ID: ép bằng `--id-col "Tên cột"`.

## Cột so sánh / compare columns
- Mặc định: mọi cột **có mặt ở cả hai file** trừ cột ID.
- Giới hạn bằng `--compare-cols Type,Level,Comments` để chỉ soi thay đổi quan tâm.
- Nên xuất **cùng bộ cột & cùng thứ tự** cho cả hai phiên bản.

## Xuất từ Revit / exporting from Revit
1. **Schedule**: tạo schedule theo category, bật cột *Element ID* (hoặc thêm
   shared parameter chứa UniqueId), Export → CSV.
2. **Dynamo/pyRevit**: `FilteredElementCollector` → ghi `el.Id`/`el.UniqueId`,
   `Category.Name`, `Type`, `Level`, tham số cần theo dõi ra CSV.

## Mẹo / tips
- Xuất snapshot mỗi mốc phát hành (v1, v2…) rồi lưu lại để so về sau.
- Kết hợp `revit-warnings-audit` / `revit-model-audit` để hiểu thay đổi ảnh hưởng
  sức khoẻ model thế nào.
