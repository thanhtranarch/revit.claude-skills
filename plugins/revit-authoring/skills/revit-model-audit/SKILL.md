---
name: revit-model-audit
description: Run a structured Revit model health audit — a checklist for file size, warnings count, purgeable elements, CAD imports, in-place families, unused view templates/filters, groups, and worksharing hygiene, with the specific Revit commands to check each and the thresholds that signal a problem. Use when a model is slow or bloated, before a milestone issue, or when setting up a model-health routine. Triggers on "model audit", "model health", "Revit slow", "file too big", "purge unused", "model cleanup", "kiểm tra sức khoẻ model", "model chậm".
---

# Revit Model Audit — Kiểm tra sức khoẻ model

Checklist audit sức khoẻ model Revit: dung lượng file, số warning, phần tử có
thể purge, CAD import, in-place family, view template/filter thừa, group,
worksharing — kèm lệnh kiểm tra và ngưỡng cảnh báo.
A structured Revit model-health checklist with the commands and thresholds.

## Khi nào dùng / When to use
- Model chậm/nặng bất thường, hoặc trước mốc phát hành.
- Thiết lập quy trình kiểm tra model health định kỳ.

## Cách dùng / How to use
Đi theo `references/model-health-checklist.md` theo thứ tự (tác động lớn trước).
Với từng mục: lệnh kiểm tra trong Revit, ngưỡng "đỏ", và cách xử lý.

Kết hợp / combine with:
- `revit-warnings-audit` — định lượng & ưu tiên warning từ file export.
- `revit-script-helper` — sinh script dọn dẹp hàng loạt (khi cần chạy trong Revit).

## Các trục kiểm chính / main axes
1. **File size & performance** — dung lượng, thời gian mở/đồng bộ.
2. **Warnings** — tổng số & số nghiêm trọng (dùng skill warnings-audit).
3. **Purge** — vật liệu/family/nhóm không dùng.
4. **CAD imports** — import (thay vì link) làm phình file, "exploded" CAD.
5. **In-place families** — nặng, khó tái dùng; hạn chế.
6. **View templates/filters/unused views** — thừa gây rối.
7. **Groups** — group lồng/ nhiều instance lệch.
8. **Worksharing** — worksets hợp lý, không "editable" tràn lan.

## Đầu ra / Output
- Bảng đánh giá theo checklist: mục · trạng thái · ghi chú · việc cần làm.
- (Không kèm script chạy ngoài Revit — đây là skill hướng dẫn + phối hợp.)

## Ghi chú / Notes
- Ngưỡng trong checklist là gợi ý; điều chỉnh theo quy mô dự án & phần cứng.
