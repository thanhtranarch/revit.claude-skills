# ACC / BIM360 Issues import — column mapping

`build_issue_log.py --acc-csv` xuất CSV với các cột phổ biến của bản import Issues.
Tuỳ template dự án, bạn có thể cần thêm/bớt cột trong ACC.

| Cột ACC (xuất) | Nguồn / mapped from | Ghi chú |
|----------------|---------------------|---------|
| `Title` | `title` | Mô tả ngắn của issue/clash. |
| `Description` | `[id] discipline` | Ghép mã clash + bộ môn để truy vết. |
| `Status` | `status` | Ánh xạ sang trạng thái ACC (Open/Closed…) nếu cần. |
| `Assignee` | `owner` | Tên/email người phụ trách theo user ACC. |
| `Location` | `location` | Grid/Level/Zone/Room. |
| `Due Date` | `target_date` | Định dạng ngày theo yêu cầu ACC. |

## Cột đầu vào (alias tự dò) / input columns
- **id**: Clash ID, Clash Name, Issue ID, Name, No, Ref.
- **title**: Description, Title, Subject, Issue, Clash.
- **discipline**: Discipline(s), Trade, Category, Clash Group, Type.
- **owner**: Owner, Assignee, Assigned To, Responsible.
- **status**: Status, State, Issue Status.
- **priority**: Priority, Severity, Importance.
- **location**: Location, Grid, Level, Zone, Area, Room.
- **raised_date**: Raised, Date, Created, Found Date, Identified.
- **target_date**: Target, Target Date, Due, Due Date, Deadline.
- **closed_date**: Closed, Closed Date, Resolved Date.

## Quy trình gộp nhiều vòng / multi-round merge
1. Mỗi vòng họp export một CSV (giữ cùng `id` cho cùng một clash).
2. Chạy `build_issue_log.py round1.csv round2.csv …` — file **sau** đè file trước
   (trạng thái mới nhất thắng), nhưng `raised_date` giữ giá trị sớm nhất.
3. Issue không có `id` được gán id tự động theo `<tên_file>#<n>`.
4. Xuất `--acc-csv` để đẩy lên ACC; xuất `--csv` để lưu lịch sử log.
