# Revit Model Health Checklist

Theo thứ tự tác động lớn → nhỏ. Với mỗi mục: **cách kiểm** · **ngưỡng đỏ** ·
**xử lý**.

## 1. File size & performance
- Kiểm: dung lượng `.rvt`; thời gian mở/Sync; **Manage > Performance** (nếu có).
- Ngưỡng đỏ: file model đơn > ~300 MB; Sync > vài phút; mở > 5–10 phút.
- Xử lý: chạy các mục dưới (purge, CAD, warnings), audit khi Open (*Open >
  Audit*), cân nhắc tách model theo khối/bộ môn.

## 2. Warnings
- Kiểm: **Manage > Warnings**; Export ra HTML rồi dùng skill `revit-warnings-audit`.
- Ngưỡng đỏ: > ~1.000 warning, hoặc nhiều HIGH (duplicate/overlap/not enclosed).
- Xử lý: ưu tiên nhóm HIGH; sửa từ nguyên nhân (duplicate mark, identical instances).

## 3. Purge unused
- Kiểm: **Manage > Purge Unused** (xem danh sách trước khi xoá).
- Ngưỡng đỏ: hàng nghìn mục purge được.
- Xử lý: purge 2–3 lần (một số phụ thuộc nhau); giữ lại thứ tiêu chuẩn công ty.

## 4. CAD imports
- Kiểm: **Manage > Manage Images / Insert > Import**; tìm *Imported* (không phải
  *Linked*) CAD; tìm CAD bị "explode".
- Ngưỡng đỏ: có Import CAD trong model chính; CAD exploded → hàng nghìn line style.
- Xử lý: đổi Import → **Link CAD**; xoá CAD thừa; dọn line pattern/text style lạ.

## 5. In-place families
- Kiểm: schedule theo *Family: In-Place*; hoặc filter theo category.
- Ngưỡng đỏ: nhiều in-place lặp lại (nên là loadable family).
- Xử lý: chuyển thành loadable family khi lặp lại; hạn chế tạo mới.

## 6. View templates / filters / unused views
- Kiểm: **View > View Templates**; số view không đặt lên sheet.
- Ngưỡng đỏ: hàng trăm view "mồ côi", filter/template trùng lặp.
- Xử lý: dùng view template thống nhất; xoá view/filter không dùng.

## 7. Groups
- Kiểm: **Model Groups** trong Project Browser; số instance & mức lồng.
- Ngưỡng đỏ: group lồng nhiều tầng; nhiều instance bị "excluded/edited".
- Xử lý: cân nhắc thay group bằng link/assembly; giải phóng group không cần.

## 8. Worksharing
- Kiểm: **Collaborate > Worksets**; ai đang "editable" cái gì.
- Ngưỡng đỏ: một người chiếm nhiều workset editable; workset đặt tên tuỳ tiện.
- Xử lý: chuẩn hoá tên workset theo bộ môn/khối; nhả quyền editable sau khi xong.

---
### Mẫu bảng đánh giá / audit table template
| # | Mục | Trạng thái | Số liệu | Việc cần làm |
|---|-----|-----------|---------|--------------|
| 1 | File size | 🔴/🟡/🟢 | … MB | … |
| 2 | Warnings | | … (HIGH …) | dùng warnings-audit |
| 3 | Purge | | … mục | purge |
| … | | | | |
