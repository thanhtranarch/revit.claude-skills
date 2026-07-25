---
name: clash-report-analysis
description: Analyzes and summarizes Navisworks clash detection reports (XML export from Clash Detective). Use when the user has a Navisworks clash report (.xml) and wants it grouped by clash test / status / discipline, prioritized, deduplicated, or summarized into an issue list for coordination meetings. Triggers on "clash report", "Navisworks clash", "check clash", "clash matrix", "báo cáo clash", "kiểm tra va chạm".
license: MIT
---

# Clash Report Analysis — Phân tích báo cáo clash (Navisworks)

Tóm tắt và ưu tiên hoá báo cáo clash xuất từ **Navisworks Clash Detective**
(XML) để phục vụ họp coordination.
Summarize & prioritize a Navisworks Clash Detective XML report for
coordination meetings.

## Khi nào dùng / When to use
- Có file XML xuất từ Navisworks (Clash Detective → Report → XML).
- Cần: gom theo clash test, đếm theo trạng thái (New/Active/Reviewed/Approved/
  Resolved), tách theo mức độ, hoặc rút gọn thành danh sách issue để giao việc.

## Cách làm / How to use
1. Xuất report: trong Navisworks, **Clash Detective → Report tab → Report Type:
   XML → Write Report**. Chọn "All tests" nếu muốn gộp.
2. Chạy script:
   ```bash
   python scripts/parse_clash.py <clash_report.xml>
   # xuất CSV register để đưa vào Excel/BIM360:
   python scripts/parse_clash.py <clash_report.xml> --csv out/clash_register.csv
   ```
3. Đọc phần tóm tắt (theo test & theo trạng thái), rồi dùng CSV để giao việc.

Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/parse_clash.py assets/sample_clash.xml
```

## Ưu tiên hoá / Prioritization guidance
Khi rút gọn thành danh sách việc, ưu tiên theo thứ tự:
1. **Trạng thái**: New/Active trước; bỏ qua Approved/Resolved.
2. **Hệ va chạm**: kết cấu ↔ MEP thường ưu tiên hơn MEP ↔ MEP nhỏ.
3. **Số lượng theo test**: test nhiều clash → dấu hiệu lệch mô hình/level, xử lý gốc.

## Đầu ra / Output
- Bảng tóm tắt số clash theo **clash test** và theo **trạng thái**.
- (Tuỳ chọn) CSV register: mỗi dòng một clash (name, test, status, distance,
  grid location, hai item va chạm) để nhập Excel hoặc ACC/BIM360 Issues.

## Ghi chú / Notes
- Script chỉ dùng thư viện chuẩn (`xml.etree`), không cần cài thêm.
- Định dạng XML của Navisworks có thể khác theo phiên bản; script đọc linh hoạt
  theo các thẻ `clashtest`, `clashresult`, `clashobjects`. Xem `references/`.
