# Bộ skill Cost / QS — `cost-qs`

Bộ **Claude Skills** cho bóc tách khối lượng & kiểm soát chi phí (QS). Đọc trực
tiếp file schedule/BoQ export (CSV) — **chạy được ngoài phần mềm**, chỉ thư viện
chuẩn.

## Skill trong bộ / skills in this set
| Skill | Trạng thái | Làm gì |
|-------|-----------|--------|
| `quantity-takeoff` | ✅ chạy được | Gom & cộng khối lượng theo nhóm (count/area/volume/length/weight) |
| `boq-compare` | ✅ chạy được | So 2 bản BoQ/takeoff: item thêm/bớt, Δ khối lượng & tổng giá trị |

## Cài đặt / install (Claude Skills)
```bash
cp -r skills/cost-qs/quantity-takeoff ~/.claude/skills/
cp -r skills/cost-qs/boq-compare      ~/.claude/skills/
# hoặc cho riêng một dự án:
cp -r skills/cost-qs/<skill> <project>/.claude/skills/
```
Hoặc nhờ Claude: *"Cài bộ skill trong `skills/cost-qs/` vào `~/.claude/skills/`."*

## Dùng thử / try it
```bash
python quantity-takeoff/scripts/takeoff.py \
       quantity-takeoff/assets/sample_quantities.csv

python boq-compare/scripts/compare_boq.py \
       boq-compare/assets/sample_boq_v1.csv boq-compare/assets/sample_boq_v2.csv
```

## Ghi chú / notes
- Đơn vị do bạn giữ nhất quán ở nguồn; công cụ chỉ cộng/so, không đổi đơn vị.
- Luồng gợi ý: `revit-authoring/schedule-qa` (làm sạch schedule) →
  `quantity-takeoff` (bóc tách) → `boq-compare` (so revision).
- Đã qua `validate_skill.py` + `audit_skill.py` (0 finding HIGH).
