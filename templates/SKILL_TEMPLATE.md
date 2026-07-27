---
name: your-skill-name
description: One or two sentences describing WHAT this skill does and WHEN Claude should use it, plus trigger keywords. Keep it specific — this is how Claude decides to load the skill. Nêu rõ chức năng + khi nào dùng + từ khoá kích hoạt (song ngữ nếu được).
# status: scaffold   # bỏ comment nếu skill chưa hoàn thiện
# allowed-tools: Read, Bash   # tuỳ chọn: giới hạn công cụ skill được dùng
---

# Skill Name — Tên skill (song ngữ)

Một đoạn ngắn nói skill này giúp gì.
A short paragraph on what this skill helps with.

## Khi nào dùng / When to use
- Liệt kê tình huống cụ thể kích hoạt skill.

## Cách dùng / How to use
1. Bước thực hiện.
2. Nếu có script:
   ```bash
   python scripts/your_script.py <input>
   ```
3. Thử nhanh với dữ liệu mẫu trong `assets/` nếu có.

## Đầu ra / Output
- Mô tả kết quả trả về.

## Tài nguyên / Resources (tuỳ chọn)
- `scripts/` — mã chạy được (chỉ dùng thư viện đã khai báo ở requirements.txt).
- `references/` — ghi chú/tài liệu tham khảo.
- `assets/` — dữ liệu mẫu để test.
- `templates/` — mẫu file để người dùng chỉnh.

## Ghi chú / Notes
- Đặt skill trong `plugins/<bộ>/skills/<tên-skill>/` (mỗi bộ = 1 plugin). Nếu là
  bộ mới, thêm plugin vào `.claude-plugin/marketplace.json`.
- Không đưa lệnh nguy hiểm, gọi mạng ngoài, hay đọc secret vào skill.
- Chạy `python scripts/validate_skill.py` và `python scripts/audit_skill.py`
  trỏ vào thư mục skill (+ `validate_marketplace.py`) trước khi mở PR.
