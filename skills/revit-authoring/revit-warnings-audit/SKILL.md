---
name: revit-warnings-audit
description: Parse a Revit warnings export (the HTML file from Manage > Warnings > Export) and turn hundreds of raw warnings into a prioritized, grouped summary — counts by warning type, most frequent messages, and a severity bucket (high/medium/low) so the team knows what to fix first. Use when a model has many warnings and the user wants them triaged, counted, grouped, or prioritized. Triggers on "Revit warnings", "review warnings", "warnings export", "too many warnings", "triage warnings", "kiểm tra warning Revit", "tổng hợp warning".
---

# Revit Warnings Audit — Tổng hợp & ưu tiên warning

Biến hàng trăm warning thô (file HTML xuất từ *Manage > Warnings > Export*)
thành báo cáo gom nhóm, ưu tiên: đếm theo loại, message hay gặp nhất, và phân
mức nghiêm trọng để biết sửa cái nào trước.
Triage a Revit warnings HTML export into a grouped, prioritized summary.

## Khi nào dùng / When to use
- Model có quá nhiều warning, cần phân loại và ưu tiên xử lý.
- Muốn theo dõi số warning theo loại qua các mốc thời gian.

## Cách dùng / How to use
1. Trong Revit: **Manage > Warnings** (Review Warnings) → **Export…** ra `.html`.
2. Chạy:
   ```bash
   python scripts/parse_warnings.py <warnings.html>
   python scripts/parse_warnings.py <warnings.html> --csv out/warnings.csv
   ```
   Thử nhanh với mẫu / quick test:
   ```bash
   python scripts/parse_warnings.py assets/sample_warnings.html
   ```

## Cách ưu tiên / prioritization
Script gán mức theo từ khoá trong message (điều chỉnh trong
`references/severity-buckets.md`):
- **HIGH** — sai lệch dữ liệu/hình học: duplicate, overlap, "identical instances",
  wall/room không khép kín, elements join.
- **MEDIUM** — cảnh báo mô hình: mismatch, slightly off axis…
- **LOW** — thẩm mỹ/nhỏ nhặt còn lại.

## Đầu ra / Output
- Tổng số warning + số nhóm message.
- Bảng theo mức nghiêm trọng và top message hay gặp nhất.
- (Tuỳ chọn) CSV: mỗi nhóm một dòng (message, count, severity).

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`html.parser`).
- Định dạng HTML export khác nhẹ theo phiên bản Revit; parser đọc theo bảng và
  gom theo dòng message — xem `references/` nếu cần chỉnh.
