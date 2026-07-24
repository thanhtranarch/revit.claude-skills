# Contributing — Đóng góp skill

Cảm ơn bạn đóng góp cho **t3lab-claude-skills**! Repo này là thư viện skill cho
Claude dùng trong ngành ACE/AEC. Vì skill có thể chứa **script chạy được** và
**chỉ dẫn Claude sẽ làm theo**, mọi đóng góp phải qua kiểm định bảo mật trước
khi merge. Đọc `docs/security-model.md` để hiểu vì sao.

## Quy trình nhanh / quick flow
1. Tạo branch từ `main`.
2. Copy `templates/SKILL_TEMPLATE.md` vào `skills/<bộ>/<tên-skill>/SKILL.md`.
3. Viết skill (song ngữ Việt–Anh nếu được). Kèm `scripts/`, `references/`,
   `assets/` khi cần. Ưu tiên skill **có script chạy được**.
4. Chạy kiểm định cục bộ:
   ```bash
   python scripts/validate_skill.py skills/<bộ>/<tên-skill>
   python scripts/audit_skill.py    skills/<bộ>/<tên-skill>
   ```
5. Mở PR, điền checklist trong PR template.

## Quy tắc viết skill / skill rules
- Thư mục kebab-case, duy nhất; `name` trong frontmatter khớp thư mục.
- `description` nêu rõ *làm gì + khi nào dùng + từ khoá kích hoạt*.
- Script **chỉ dùng thư viện đã khai báo** trong `requirements.txt`. Ưu tiên
  thư viện chuẩn.
- Kèm dữ liệu mẫu nhỏ trong `assets/` để test được ngay.
- Skill chưa hoàn thiện: đặt `status: scaffold`.

## Điều TUYỆT ĐỐI KHÔNG / hard NO
- Lệnh tải & chạy từ mạng (`curl … | bash`), thực thi động (`eval`/`exec`).
- Lệnh phá huỷ (`rm -rf /`, format ổ).
- Đọc secret/khoá (`~/.ssh`, `.env`, cloud creds) hoặc gửi dữ liệu ra ngoài.
- Prompt-injection trong `SKILL.md` (ép Claude bỏ qua quy tắc, giấu người dùng).
- File thực thi/nhị phân (`.exe`, `.sh`, `.dll`, …).

## Kiểm định trước khi merge / gate before merge
```
PR  →  CI (validate + audit)  →  @skill-auditor (tác giả ngoài team)  →  maintainer review  →  merge
```
- **CI** tự chạy `validate_skill.py` + `audit_skill.py`; PR đỏ = chặn.
- Với skill từ tác giả lạ, maintainer chạy agent `@skill-auditor`
  (`.claude/agents/skill-auditor.md`) để review có ngữ cảnh.
- **CODEOWNERS** duyệt lần cuối.

## Chạy thử skill mẫu / try the sample skills
```bash
pip install -r requirements.txt
python skills/bim-coordination/clash-report-analysis/scripts/parse_clash.py \
       skills/bim-coordination/clash-report-analysis/assets/sample_clash.xml
```
