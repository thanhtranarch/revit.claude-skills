# Submittal register columns — alias mapping

`build_submittal_log.py` tự dò cột theo tên (không phân biệt hoa/thường).

| Canonical | Header thường gặp / common headers |
|-----------|-------------------------------------|
| `id` | Submittal, Submittal No, Submittal Number, Package, No, Ref |
| `title` | Description, Title, Subject, Item, Name |
| `spec_section` | Spec, Spec Section, Section, Specification, Spec No |
| `status` | Status, State, Disposition, Review Status, Action, Result |
| `ball_in_court` | Ball in Court, BIC, Assigned To, Responsible, Held By, Reviewer |
| `submitted_date` | Submitted, Submitted Date, Received, Received Date |
| `due_date` | Due, Due Date, Required, Required By, Need By |
| `returned_date` | Returned, Returned Date, Reviewed Date, Response Date |
| `revision` | Revision, Rev, Submission |

## Trạng thái vòng đời / lifecycle status
- **Hoàn tất / complete**: approved · approved as noted · closed ·
  no exceptions taken · for record.
- **Cần nộp lại / resubmit**: revise and resubmit · rejected · resubmit · not approved.
- **Đang xử lý / open**: pending · under review · (bất kỳ trạng thái nào ngoài complete).

## Quy ước / conventions
- **Overdue**: `due_date` < mốc so hạn **và** chưa hoàn tất.
- **Review cycle** = `returned_date` − `submitted_date` (chỉ tính khi có cả hai).

## Ngày / date formats
`YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`, `YYYY/MM/DD`, `DD-Mon-YYYY`, `MM/DD/YY`.
