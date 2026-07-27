# Contributing — Đóng góp skill

Cảm ơn bạn đóng góp cho **t3lab-claude-skills**! Repo này là thư viện skill cho
Claude dùng trong ngành ACE/AEC. Vì skill có thể chứa **script chạy được** và
**chỉ dẫn Claude sẽ làm theo**, mọi đóng góp phải qua kiểm định bảo mật trước
khi merge. Đọc `docs/security-model.md` để hiểu vì sao.

## Quy trình nhanh / quick flow
1. Tạo branch từ `main`.
2. Copy `templates/SKILL_TEMPLATE.md` vào `skills/<software>/<tên-skill>/SKILL.md`
   (nhóm theo **phần mềm**: `revit`, `navisworks`, `acc-bim360`, `bluebeam-pdf`,
   `office-data`). Skill Revit đặt tên theo *Quy ước đặt tên skill Revit* bên dưới
   (`rv-`/`rvarc-`/`rvstr-`/`rvmep-` + đúng 2 đoạn).
3. Viết skill (song ngữ Việt–Anh nếu được). Kèm `scripts/`, `references/`,
   `assets/` khi cần. Ưu tiên skill **có script chạy được**.
4. Gắn `metadata` (`software`, `discipline`, `category`) — xem giá trị hợp lệ ở
   đầu `scripts/build_taxonomy.py` — rồi sinh lại bảng tra cứu:
   ```bash
   python scripts/validate_marketplace.py
   python scripts/validate_skill.py plugins/<plugin>/skills/<tên-skill>
   python scripts/audit_skill.py    plugins/<plugin>/skills/<tên-skill>
   ```
5. Chạy kiểm định cục bộ:
   ```bash
   python scripts/validate_skill.py skills/<software>/<tên-skill>
   python scripts/audit_skill.py    skills/<software>/<tên-skill>
   ```
6. Mở PR, điền checklist trong PR template.

## Quy tắc viết skill / skill rules
- Thư mục kebab-case, duy nhất; `name` trong frontmatter khớp thư mục (≤64 ký tự).
- `description` (≤1024 ký tự) viết **ngôi thứ ba**, nêu rõ *làm gì* + *khi nào
  dùng* (`Use when …`) + *từ khoá kích hoạt*. VD: `Analyzes …. Use when …. Triggers on …`.
- Trường tuỳ chọn theo spec: `license`, `compatibility` (≤500 ký tự),
  `metadata` (map chuỗi→chuỗi), `allowed-tools`. **Không** thêm key top-level
  ngoài spec (validator sẽ cảnh báo).
- Script **chỉ dùng thư viện đã khai báo** trong `requirements.txt`. Ưu tiên
  thư viện chuẩn.
- Kèm dữ liệu mẫu nhỏ trong `assets/` để test được ngay.
- Skill chưa hoàn thiện: đặt `status: scaffold` **trong `metadata`**.

## Quy ước đặt tên skill Revit / Revit skill naming (bắt buộc)
Skill Revit (`metadata.software: revit`) đặt tên **theo bộ môn**, dạng
`<prefix>-<đoạn1>-<đoạn2>` — **prefix bộ môn + đúng 2 đoạn** kebab-case. Luật này
được `scripts/validate_skill.py` kiểm tự động, CI sẽ **chặn** nếu sai.

| Prefix | Bộ môn / discipline | `metadata.discipline` | Ví dụ |
|--------|---------------------|-----------------------|-------|
| `rv-`    | Revit chung / đa bộ môn (general) | `multi`        | `rv-schedule-qa`, `rv-batch-export` |
| `rvarc-` | Revit Kiến trúc / Architecture    | `architecture` | *(để dành cho skill Kiến trúc)* |
| `rvstr-` | Revit Kết cấu / Structural        | `structural`   | `rvstr-beam-cad`, `rvstr-column-tools` |
| `rvmep-` | Revit MEP                         | `mep`          | `rvmep-duct-velocity` |

**Quy tắc / rules**
1. **Prefix theo bộ môn chính.** Skill dùng được cho mọi bộ môn → `rv-`; chỉ dùng
   `rvarc-/rvstr-/rvmep-` khi skill *đặc thù* bộ môn đó.
2. **Prefix phải khớp `metadata.discipline`** (rv↔multi, rvarc↔architecture,
   rvstr↔structural, rvmep↔mep) — sai khớp là lỗi.
3. **Đúng 2 đoạn sau prefix** `<prefix>-<a>-<b>`: không 1 đoạn, không 3+ đoạn.
   Rút gọn phần mô tả cho vừa 2 đoạn (vd `beam-from-cad` → `rvstr-beam-cad`).
4. **Tên thư mục = `name`** trong frontmatter (kebab-case, ≤64 ký tự).
5. Bộ môn chưa có prefix riêng (vd Civil) → tạm dùng `rv-` và nêu trong PR.

**Khi thêm/sửa skill Revit / when adding or updating a Revit skill**
- Chọn prefix theo bộ môn và đặt `metadata.discipline` khớp.
- Nếu skill có bản published trong `plugins/`, đổi tên **cả** `skills/<…>` lẫn
  `plugins/<…>/skills/<…>` cho đồng bộ.
- Skill *ghi vào Revit* (MCP/pyRevit/Dynamo) phải khai báo `compatibility` rõ
  (vd `Requires Revit MCP connector`) — xem `docs/roadmap.md`.
- Chạy `python scripts/build_taxonomy.py` để cập nhật 3 bảng tra cứu.

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
python plugins/bim-coordination/skills/clash-report-analysis/scripts/parse_clash.py \
       plugins/bim-coordination/skills/clash-report-analysis/assets/sample_clash.xml
```

## License của phần đóng góp / contribution license
Khi mở PR, bạn đồng ý phát hành phần đóng góp theo giấy phép **MIT** của project
(xem [`LICENSE`](LICENSE)) — inbound = outbound. Chỉ đóng góp nội dung bạn có
quyền cấp phép.
By submitting a PR you agree to license your contribution under the project's
MIT License.
