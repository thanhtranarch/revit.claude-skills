# Change order register columns — alias mapping

`track_change_orders.py` tự dò cột theo tên (không phân biệt hoa/thường).

| Canonical | Header thường gặp / common headers |
|-----------|-------------------------------------|
| `id` | CO, CO No, CO Number, Change Order, Variation, PCO, Number, Ref |
| `title` | Description, Title, Subject, Name |
| `status` | Status, State, Disposition |
| `discipline` | Discipline, Trade, Type, Category |
| `initiator` | Requested By, Originator, Raised By, Initiator, Source |
| `submitted_date` | Submitted, Submitted Date, Date Submitted, Created, Raised |
| `due_date` | Due, Due Date, Response Due, Required By |
| `approved_date` | Approved, Approved Date, Decision Date, Closed Date |
| `cost_amount` | Cost, Cost Amount, Amount, Value, Cost Impact, $ |
| `schedule_days` | Schedule Days, Time Impact, Schedule Impact, Days, EOT |
| `reason` | Reason, Justification, Cause |

## Quy ước / conventions
- **Bucket**: `approved` ∈ {approved, approved as noted, accepted};
  `rejected` ∈ {rejected, declined, void, withdrawn}; còn lại `pending`.
- **Overdue**: `due_date` < mốc so hạn **và** đang `pending`.
- **Tiền / money**: bỏ ký hiệu tiền tệ & dấu phẩy; `(1,000)` = −1000 (deductive CO).
- **Schedule days**: lấy số nguyên đầu tiên trong ô (âm nếu có dấu `-`).

## Ngày / date formats
`YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`, `YYYY/MM/DD`, `DD-Mon-YYYY`, `MM/DD/YY`.
