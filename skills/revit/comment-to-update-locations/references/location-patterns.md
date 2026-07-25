# Location extraction — cột & mẫu nhận diện vị trí

Tham chiếu cho `comment_to_locations.py`. Skill lấy vị trí theo **2 lớp**:
1. **Cột chuyên dụng** (ưu tiên) — auto-detect theo alias.
2. **Phân tích text** comment/subject nếu cột trống — regex song ngữ EN/VI.

## Cột được dò / detected columns
| Trường | Alias (không phân biệt hoa/thường) |
|--------|------------------------------------|
| id | id, no, markup id, issue id, rfi no |
| subject | subject, title, type, category |
| text | comment, comments, description, note, detail, body, message, response |
| sheet | sheet, sheet number, page label, page, drawing |
| level | level, floor, storey, tầng |
| grid | grid, gridline, axis, trục |
| room | room, space, phòng |
| element_id | element id, elementid, elem id, revit id |
| author | author, created by, assignee, owner, raised by |
| priority | priority, severity, importance, mức độ, ưu tiên |
| status | status, state, trạng thái |

Ép cột bằng `--text-col`, `--sheet-col`, `--level-col`, `--priority-col`, `--status-col`.

## Mẫu text / free-text patterns (EN + VI)
| Loại | Bắt được ví dụ | Ghi chú |
|------|----------------|---------|
| **Grid** | `grid B-4`, `axis A/3`, `trục C-5`, `gridline 4-B` | Chữ-số hoặc số-chữ, phân cách `- / ~` |
| **Level** | `Level 2`, `L3`, `GF`, `B1`, `tầng 3` | |
| **Room** | `Room 101`, `phòng 205`, `space 3A` | |
| **Element ID** | `Element ID 348122`, `Revit ID 987654`, `ID 348122` | Yêu cầu **≥5 chữ số** để giảm nhầm |
| **Sheet** | `A-101`, `M-201`, `S-210` | Chỉ dò từ text khi không có cột sheet |

## location_source — nguồn vị trí
- `column` — hoàn toàn từ cột chuyên dụng.
- `parsed` — hoàn toàn từ phân tích text.
- `column+parsed` — vừa cột vừa text (**nên review** phần parse).
- `none` — không xác định được → cần bổ sung cột hoặc ghi rõ vị trí trong comment.

## Ranh giới với Revit / Revit-MCP boundary
Skill này (offline) cho ra **punch list + gợi ý vị trí**. Việc **định vị chính xác
trong model** — chuyển grid/level → toạ độ, hay **chọn đúng element theo ID** và
zoom tới nó — cần bước **Revit MCP / pyRevit** (xem `docs/roadmap.md`). Có thể nối
tiếp: dùng element_id ở đây làm input cho script pyRevit `SelectElementsByIds`.

## Mở rộng / extending
Thêm mẫu bằng cách sửa các hằng `RE_GRID`, `RE_LEVEL`, `RE_ROOM`, `RE_ELEM`,
`RE_SHEET` trong script; hoặc bổ sung alias cột trong `ALIASES`.
