# Plugin: `documentation-review`

Bộ **Claude Skills** cho tài liệu, markup và comment trong AEC.

## Skills
| Skill (gọi `/documentation-review:<skill>`) | Trạng thái | Làm gì |
|------|-----------|--------|
| `pdf-markup-compare` | ✅ chạy được | So sánh markup/annotation giữa 2 revision PDF (added/removed/moved) |
| `comment-aggregation` | ✅ chạy được | Gộp comment/RFI nhiều nguồn CSV → register Excel, khử trùng lặp |
| `submittal-log` | 🚧 scaffold | Nhật ký & trạng thái submittal |

## Cài đặt / install
```
/plugin marketplace add thanhtranarch/t3lab-claude-skills
/plugin install documentation-review@t3lab-ace-skills
```

## Python deps
```bash
pip install pypdf openpyxl
```
- `pdf-markup-compare` → `pypdf`
- `comment-aggregation` → `openpyxl`

## Dùng thử / try
```bash
python skills/comment-aggregation/scripts/aggregate_comments.py \
       skills/comment-aggregation/assets/*.csv -o /tmp/register.xlsx
```
