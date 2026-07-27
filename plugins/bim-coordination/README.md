# Plugin: `bim-coordination`

Bộ **Claude Skills** cho Coordination & Clash trong BIM. Cài như plugin của
Claude Code (xem gốc repo để thêm marketplace).

## Skills
| Skill (gọi `/bim-coordination:<skill>`) | Trạng thái | Làm gì |
|------|-----------|--------|
| `clash-report-analysis` | ✅ chạy được | Phân tích/tóm tắt report clash Navisworks (XML) → CSV register |
| `shared-coordinates` | ✅ hướng dẫn | Thiết lập & QA toạ độ chung (SP/PBP/north) |
| `model-federation` | 🚧 scaffold | Gộp model coordination (NWF/NWD, ACC) |
| `coordination-issue-log` | 🚧 scaffold | Biến clash thành issue log giao việc |

## Cài đặt / install
```
/plugin marketplace add thanhtranarch/t3lab-claude-skills
/plugin install bim-coordination@t3lab-ace-skills
```

## Python deps
Chỉ thư viện chuẩn — không cần cài gì thêm cho `clash-report-analysis`.

## Dùng thử / try
```bash
python skills/clash-report-analysis/scripts/parse_clash.py \
       skills/clash-report-analysis/assets/sample_clash.xml
```
