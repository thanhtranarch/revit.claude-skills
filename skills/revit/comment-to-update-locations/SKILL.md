---
name: comment-to-update-locations
description: Turns review comments, markups, and RFIs (Bluebeam / ACC / BIM360 / RFI CSV exports) into a prioritized model-update punch list — pulling the location to fix (sheet, level, grid, room, Revit element ID) from dedicated columns or by parsing the comment text in English or Vietnamese, and flagging comments whose location cannot be resolved. Use when converting a review / markup / issue export into an actionable list of where to update the Revit model, or triaging comments by location and priority before a fixing session. Triggers on "comment to locations", "markup punch list", "where to update model", "review comments to actions", "punch list", "vị trí cần update", "comment thành việc cần sửa", "xuất vị trí sửa model".
license: MIT
metadata:
  software: revit
  discipline: multi
  category: coordination
---

# Comment → Update Locations — Comment thành punch list vị trí cần sửa

Biến **comment/markup/RFI** (Bluebeam markup summary, ACC/BIM360 issues, RFI
register…) thành **punch list vị trí cần cập nhật trong model**: lấy vị trí
(sheet, level, grid, room, Revit element ID) từ **cột chuyên dụng** hoặc **phân
tích text comment** (song ngữ EN/VI), sắp theo ưu tiên, và đánh dấu comment **chưa
xác định được vị trí**.
Turns review comments into a prioritized model-update punch list with locations.

## Khi nào dùng / When to use
- Có export comment/markup/issue và cần **danh sách "ở đâu cần sửa gì"** cho model.
- Trước một buổi sửa model: **triage** comment theo vị trí + ưu tiên + ai làm.
- Muốn tách comment **có vị trí rõ** khỏi comment **chung chung** cần hỏi lại.

## Cách dùng / How to use
```bash
python scripts/comment_to_locations.py <comments.csv>

# Chỉ comment chưa đóng + xuất punch list CSV:
python scripts/comment_to_locations.py <comments.csv> --open-only --csv out/punchlist.csv

# Ép cột nếu header lạ:
python scripts/comment_to_locations.py <comments.csv> --text-col Comment --sheet-col "Page Label"
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/comment_to_locations.py assets/sample_comments.csv
```

## Đầu ra / Output
- **Punch list** sắp theo ưu tiên: id · priority · status · **location** (sheet /
  level / grid / room / element id) · comment.
- Tỉ lệ comment **xác định được vị trí**; nguồn vị trí (`column` / `parsed` /
  `column+parsed` / `none`).
- Rollup theo sheet; cảnh báo comment **chưa xác định được vị trí**.
- (Tuỳ chọn) CSV/JSON để đưa sang bước sửa hoặc import issue tracker.

## Tài nguyên / Resources
- `scripts/comment_to_locations.py` — bộ trích vị trí (chỉ stdlib).
- `references/location-patterns.md` — cột & mẫu regex EN/VI, ý nghĩa
  `location_source`, và ranh giới với **Revit MCP**.
- `assets/sample_comments.csv` — comment mẫu (Bluebeam-style, có vị trí trong text).

## Ghi chú / Notes
- Skill **offline**: cho ra punch list + gợi ý vị trí. Việc **chọn/zoom đúng
  element trong Revit** hay đổi grid→toạ độ cần bước **Revit MCP / pyRevit**
  (xem `docs/roadmap.md`) — có thể dùng `element_id` ở đây làm input cho pyRevit
  `SelectElementsByIds`.
- Element ID yêu cầu ≥5 chữ số khi parse từ text để giảm nhầm; kiểm lại cột
  `location_source = parsed` trước khi hành động.
- Kết hợp `bluebeam-pdf/comment-aggregation` (gộp nhiều nguồn) → rồi chạy skill này.
