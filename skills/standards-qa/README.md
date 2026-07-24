# Bộ skill Chuẩn & QA — `standards-qa`

Bộ **Claude Skills** kiểm tra tài liệu/dữ liệu AEC theo chuẩn: đặt tên ISO 19650,
soát chính tả, và các kiểm tra QA khác. Đều **chạy được ngoài phần mềm** — chỉ
cần một file CSV/TXT (register, sheet list, comment log…).

## Skill trong bộ / skills in this set
| Skill | Trạng thái | Làm gì |
|-------|-----------|--------|
| `iso19650-naming-check` | ✅ chạy được | Kiểm tên file theo ISO 19650 (trường, mã Type/Role, status/revision) |
| `spellcheck-review` | ✅ chạy được | Soát chính tả text AEC (lỗi thường gặp + từ lặp; `--dict` tuỳ chọn) |
| `sheet-naming-check` | ✅ chạy được | Kiểm chuẩn số/tên sheet, bắt trùng số & từ cấm (Copy/Draft…) |

## Cài đặt / install (Claude Skills)
Đặt **thư mục skill** (chứa `SKILL.md`) trực tiếp vào `~/.claude/skills/`:
```bash
cp -r skills/standards-qa/iso19650-naming-check ~/.claude/skills/
cp -r skills/standards-qa/spellcheck-review     ~/.claude/skills/
cp -r skills/standards-qa/sheet-naming-check    ~/.claude/skills/
# hoặc cho riêng một dự án:
cp -r skills/standards-qa/<skill> <project>/.claude/skills/
```
Hoặc nhờ Claude: *"Cài bộ skill trong `skills/standards-qa/` vào `~/.claude/skills/`."*

## Dùng thử / try it
```bash
python iso19650-naming-check/scripts/check_iso19650.py \
       iso19650-naming-check/assets/sample_filenames.csv

python spellcheck-review/scripts/spellcheck.py \
       spellcheck-review/assets/sample_text.csv --col Comment

python sheet-naming-check/scripts/check_sheet_naming.py \
       sheet-naming-check/assets/sample_sheets.csv
```

## Ghi chú / notes
- `iso19650-naming-check`: danh mục mã Type/Role và độ dài trường **tuỳ biến
  được** qua `--rules` (mỗi dự án/EIR khác nhau).
- `spellcheck-review`: chế độ mặc định không cần cài gì; `--dict` cần
  `pyspellchecker` (tuỳ chọn trong `requirements.txt`).
- Đã qua `validate_skill.py` + `audit_skill.py` (0 finding HIGH).
