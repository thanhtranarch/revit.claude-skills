# Plugin: `standards-qa`

Bộ **Claude Skills** kiểm tra tài liệu/dữ liệu AEC theo chuẩn: đặt tên ISO 19650,
soát chính tả, và các kiểm tra QA khác. Đều **chạy được ngoài phần mềm** — chỉ
cần một file CSV/TXT (register, sheet list, comment log…).

## Skills
| Skill (gọi `/standards-qa:<skill>`) | Trạng thái | Làm gì |
|-------|-----------|--------|
| `iso19650-naming-check` | ✅ chạy được | Kiểm tên file theo ISO 19650 (trường, mã Type/Role, status/revision) |
| `spellcheck-review` | ✅ chạy được | Soát chính tả text AEC (lỗi thường gặp + từ lặp; `--dict` tuỳ chọn) |
| `sheet-naming-check` | 🚧 scaffold | Kiểm chuẩn số/tên sheet & view, bắt trùng số |

## Cài đặt / install
```
/plugin marketplace add thanhtranarch/t3lab-claude-skills
/plugin install standards-qa@t3lab-ace-skills
/reload-plugins
```
Hoặc nhờ Claude qua chat: *"Thêm marketplace t3lab-claude-skills và cài plugin
standards-qa."*

## Python deps
Chế độ mặc định chỉ cần thư viện chuẩn. Tuỳ chọn:
```bash
pip install pyyaml          # iso19650-naming-check --rules
pip install pyspellchecker  # spellcheck-review --dict
```

## Dùng thử / try it
```bash
python skills/iso19650-naming-check/scripts/check_iso19650.py \
       skills/iso19650-naming-check/assets/sample_filenames.csv

python skills/spellcheck-review/scripts/spellcheck.py \
       skills/spellcheck-review/assets/sample_text.csv --col Comment
```

## Ghi chú / notes
- `iso19650-naming-check`: danh mục mã Type/Role và độ dài trường **tuỳ biến
  được** qua `--rules` (mỗi dự án/EIR khác nhau).
- Đã qua `validate_skill.py` + `audit_skill.py` (0 finding HIGH).
