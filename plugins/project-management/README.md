# Plugin: `project-management`

Bộ **Claude Skills** cho quản lý dự án AEC (ACC/BIM360 + Excel).

## Skills
| Skill (gọi `/project-management:<skill>`) | Trạng thái | Làm gì |
|------|-----------|--------|
| `acc-issue-register` | ✅ chạy được | Chuẩn hoá issue ACC/BIM360 (CSV) + đánh dấu quá hạn |
| `rfi-tracker` | 🚧 scaffold | Theo dõi RFI + aging |
| `weekly-report` | 🚧 scaffold | Báo cáo trạng thái tuần đa nguồn |

## Cài đặt / install
```
/plugin marketplace add thanhtranarch/t3lab-claude-skills
/plugin install project-management@t3lab-ace-skills
```

## Python deps
Chỉ thư viện chuẩn — không cần cài gì thêm cho `acc-issue-register`.

## Dùng thử / try
```bash
python skills/acc-issue-register/scripts/normalize_issues.py \
       skills/acc-issue-register/assets/sample_issues.csv --as-of 2026-07-24
```
