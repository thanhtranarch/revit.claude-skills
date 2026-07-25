# Bộ skill MEP — `mep-systems`

Bộ **Claude Skills** kiểm tra hệ thống MEP từ file schedule export (CSV) —
**chạy được ngoài phần mềm**, chỉ thư viện chuẩn.

## Skill trong bộ / skills in this set
| Skill | Trạng thái | Làm gì |
|-------|-----------|--------|
| `duct-velocity-check` | ✅ chạy được | Vận tốc & tỷ lệ cạnh ống gió; cờ vượt vận tốc / aspect |

> Bộ mới — sẽ mở rộng (pipe sizing, equipment schedule QA, connected-load…).

## Cài đặt / install (Claude Skills)
```bash
cp -r skills/mep-systems/duct-velocity-check ~/.claude/skills/
# hoặc cho riêng một dự án:
cp -r skills/mep-systems/<skill> <project>/.claude/skills/
```
Hoặc nhờ Claude: *"Cài bộ skill trong `skills/mep-systems/` vào `~/.claude/skills/`."*

## Dùng thử / try it
```bash
python duct-velocity-check/scripts/check_duct.py \
       duct-velocity-check/assets/sample_ducts.csv
```

## Ghi chú / notes
- Ngưỡng (vận tốc, aspect) chỉnh theo tiêu chuẩn dự án qua `--rules` JSON.
- Đã qua `validate_skill.py` + `audit_skill.py` (0 finding HIGH).
