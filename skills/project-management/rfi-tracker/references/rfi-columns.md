# RFI register columns — alias mapping

Script `track_rfis.py` tự dò cột theo tên (không phân biệt hoa/thường). Bảng dưới
liệt kê các cột chuẩn (canonical) và những header thường gặp từ Procore / ACC /
BIM360 / Excel. Cột thiếu để trống.

| Canonical | Header thường gặp / common headers |
|-----------|-------------------------------------|
| `id` | RFI, RFI Number, RFI ID, Number, No, Ref |
| `subject` | Subject, Title, Question, Description, Name |
| `status` | Status, State |
| `ball_in_court` | Ball in Court, Ball-in-Court, BIC, Assigned To, Responsible, Held By |
| `discipline` | Discipline, Trade, Type, Category |
| `submitted_date` | Submitted, Submitted Date, Date Submitted, Created, Opened |
| `response_due` | Response Due, Due, Due Date, Date Required, Answer Due, Required By |
| `closed_date` | Closed, Closed Date, Date Closed, Answered Date, Response Date |
| `cost_impact` | Cost Impact, Cost, $ Impact |
| `schedule_impact` | Schedule Impact, Schedule, Time Impact |

## Quy ước / conventions
- **Đóng / closed**: `status` ∈ {closed, answered, resolved, void} **hoặc** có
  `closed_date`.
- **Quá hạn / overdue**: `response_due` < mốc so hạn **và** chưa đóng.
- **Cost/schedule impact** nhận giá trị "có": yes / y / true / 1 / x / có.
- **Aging bucket** (ngày mở, chỉ RFI đang mở): `0-7`, `8-14`, `15-30`, `31+`.

## Ngày / date formats
Chấp nhận: `YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`, `YYYY/MM/DD`, `DD-Mon-YYYY`,
`MM/DD/YY`.
