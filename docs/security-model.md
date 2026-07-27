# Security Model — Kiểm định skill / Skill vetting

> Vì repo này nhận skill từ nhiều người, mọi skill phải qua kiểm định trước khi
> merge. Trang này mô tả mô hình mối đe doạ và các tầng phòng thủ.
> Because this repo accepts community skills, every skill is vetted before merge.

## Vì sao / Why
Một Claude Skill có thể chứa **script chạy được** và **chỉ dẫn mà Claude sẽ
đọc và làm theo**. Cả hai đều là bề mặt tấn công:
- Script độc → phá huỷ máy, rò rỉ dữ liệu, cài backdoor.
- Text trong `SKILL.md` → *prompt-injection*: ép Claude làm điều người dùng
  không muốn (tải & chạy payload, để lộ secret, giấu hành vi).

## Mối đe doạ / Threat model
| # | Nhóm | Ví dụ |
|---|------|-------|
| 1 | Remote code execution | `curl … \| bash`, `IEX(DownloadString)`, base64→sh |
| 2 | Destructive | `rm -rf /`, `mkfs`, `dd if=`, format/ghi đè ổ |
| 3 | Exfiltration | đọc `~/.ssh`, `.env`, cloud creds, `*_TOKEN/SECRET`; gửi ra host lạ |
| 4 | Dynamic exec / obfuscation | `eval`/`exec`, `pickle.loads`, base64 dài, Unicode ẩn |
| 5 | Prompt-injection | "ignore previous", "don't tell the user", "disable safety" |
| 6 | Over-broad scope | xin `allowed-tools` / quyền mạng ngoài chức năng khai báo |
| 7 | Mô tả sai | `description` khác với hành vi thật của code |

## Các tầng phòng thủ / Defense layers
1. **`scripts/validate_skill.py`** — cấu trúc & metadata: có `SKILL.md`,
   frontmatter hợp lệ (`name`, `description`), `name` khớp thư mục, chặn file
   thực thi/nhị phân & file quá lớn. Exit ≠ 0 nếu có lỗi.
2. **`scripts/audit_skill.py`** — quét tĩnh (regex + AST) phát hiện nhóm 1–5
   với mức HIGH/MEDIUM/LOW. Exit ≠ 0 khi vượt ngưỡng (mặc định: có HIGH).
3. **Agent `skill-auditor`** (`.claude/agents/skill-auditor.md`) — rà soát thủ
   công có ngữ cảnh (nhóm 6–7 và mã tinh vi mà regex bỏ sót). Verdict PASS/FAIL.
4. **CI `.github/workflows/skill-validation.yml`** — chạy tầng 1–2 + kiểm
   manifest (`validate_marketplace.py`) tự động trên mọi PR đụng `plugins/**`
   hoặc `.claude-plugin/**`; PR đỏ nếu vi phạm.
5. **`CODEOWNERS` + review người thật** — maintainer duyệt lần cuối trước merge.

Không tầng nào là tuyệt đối — chúng bổ trợ nhau (defense in depth). Tầng tự
động (1–2) là bắt buộc; agent (3) khuyến nghị cho skill từ tác giả lạ.

## Quy trình duyệt / Review flow
```
PR mở  ──►  CI: validate + audit  ──►  skill-auditor (tác giả lạ)  ──►  maintainer review  ──►  merge
             (fail = chặn)              (verdict FAIL = chặn)            (CODEOWNERS)
```

## Chạy cục bộ / Run locally
```bash
python scripts/validate_skill.py plugins/<plugin>/skills/<skill>
python scripts/audit_skill.py    plugins/<plugin>/skills/<skill>
# hoặc quét toàn bộ / or scan everything:
python scripts/validate_marketplace.py
python scripts/validate_skill.py plugins
python scripts/audit_skill.py    plugins
```
Trong Claude Code, gọi agent: `@skill-auditor` trỏ vào thư mục skill cần duyệt.

## Giới hạn / Limitations
- Quét tĩnh không phát hiện được mọi mã độc (obfuscation nâng cao, logic phụ
  thuộc dữ liệu runtime). Vì vậy vẫn cần agent + người review.
- Auditor **không chạy** code của skill. Không tự ý thực thi script chưa duyệt.
- Cập nhật rule trong `scripts/audit_skill.py` khi có mẫu tấn công mới.
