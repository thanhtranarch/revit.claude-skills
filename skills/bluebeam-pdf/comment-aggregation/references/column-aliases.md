# Column aliases — ánh xạ cột nguồn / source-header mapping

Script `aggregate_comments.py` chuẩn hoá tên cột (không phân biệt hoa/thường)
về 8 cột chuẩn. Bảng dưới liệt kê alias mặc định — thêm alias bằng cách sửa
`COLUMN_ALIASES` trong script.

| Cột chuẩn | Alias chấp nhận |
|-----------|-----------------|
| `id` | id, no, number, issue id, markup id |
| `subject` | subject, title, topic |
| `comment` | comment, comments, description, contents, details, text, notes |
| `author` | author, created by, assignee, reviewer |
| `discipline` | discipline, trade, category, type |
| `status` | status, state |
| `location` | location, sheet, page, space, grid |
| `date` | date, created at, created, due date |

## Nguồn thường gặp / common sources
- **Bluebeam** — Markup Summary → CSV: cột `Subject`, `Comments`, `Author`,
  `Page`, `Status`.
- **ACC / BIM360 Issues** — export CSV: `Issue ID`, `Title`, `Description`,
  `Assignee`, `Status`, `Location`, `Due date`.
- **Bảng reviewer tự lập** — đặt header khớp một trong các alias ở trên là được.
