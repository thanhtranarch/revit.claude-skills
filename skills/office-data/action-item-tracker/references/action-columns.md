# Action item register columns — alias mapping

`track_actions.py` tự dò cột theo tên (không phân biệt hoa/thường).

| Canonical | Header thường gặp / common headers |
|-----------|-------------------------------------|
| `id` | Item, Action ID, No, Number, Ref, # |
| `action` | Action, Action Item, Task, Description, Title, Detail(s) |
| `owner` | Owner, Assignee, Assigned To, Responsible, Who, By Whom |
| `status` | Status, State |
| `meeting` | Meeting, Meeting ID, Meeting Date, Source, Minutes, Topic |
| `priority` | Priority, Importance, Severity |
| `raised_date` | Raised, Raised Date, Date Raised, Created, Opened, Date |
| `due_date` | Due, Due Date, Target, Target Date, Deadline, By When |
| `closed_date` | Closed, Closed Date, Completed Date, Done Date |

## Quy ước / conventions
- **Đóng / closed**: status ∈ {closed, done, complete, completed, resolved,
  cancelled, canceled} **hoặc** có `closed_date`.
- **Quá hạn / overdue**: `due_date` < mốc so hạn **và** chưa đóng.
- **Aging bucket** (ngày mở, chỉ item đang mở): `0-7`, `8-14`, `15-30`, `31+`.

## Ngày / date formats
`YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`, `YYYY/MM/DD`, `DD-Mon-YYYY`, `MM/DD/YY`.
