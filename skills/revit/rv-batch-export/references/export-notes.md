# Export notes — khác biệt định dạng & phiên bản

## PDF
- **Revit 2022+**: có API export PDF gốc — `PDFExportOptions` + `doc.Export(dir,
  [sheetIds], opts)`. Xem `templates/pyrevit_batch_export_sheets.py`.
- **Revit ≤ 2021**: không có API PDF gốc → in qua máy in PDF (đặt printer mặc
  định, dùng `PrintManager`), hoặc dùng addin bên thứ ba.
- Mỗi sheet 1 file: `opts.Combine = False`. Gộp 1 file: `Combine = True`.

## DWG / DWF
- `DWGExportOptions` + `doc.Export(dir, name, [viewIds], opts)`.
- Chú ý mapping layer (Export Layers standard) để đúng chuẩn CAD.

## NWC (Navisworks)
- Cần **Navisworks NWC exporter** cài kèm Revit. Export qua add-in
  (`Export > NWC`) hoặc `doc.Export` với NavisworksExportOptions (nếu có).
- Dùng cho coordination → nối vào skill `bim-coordination`.

## IFC
- `IFCExportOptions`; chọn schema (IFC2x3 / IFC4) và MVD phù hợp yêu cầu dự án.

## Quy ước đặt tên / naming
- Mẫu mặc định `{SheetNumber}-{SheetName}-{Revision}`.
- Luôn thay ký tự không hợp lệ trên Windows: `\ / : * ? " < > |` → `_`.
- Nếu phát hành theo revision, lấy **Current Revision** của sheet; sheet chưa có
  revision → gán mặc định (vd `A`) hoặc bỏ hậu tố.

## An toàn / safety
- Export chỉ đọc model + ghi file → **không cần Transaction**.
- Kiểm tra thư mục đích tồn tại, quyền ghi và dung lượng trước khi chạy loạt lớn.
- Thử với 1–2 sheet trước khi export toàn bộ set.
