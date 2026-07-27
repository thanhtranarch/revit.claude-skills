---
name: your-skill-name
description: Third-person summary of WHAT this skill does, then a "Use when …" clause for WHEN Claude should load it, plus trigger keywords. Đây là cách Claude quyết định nạp skill — viết ngôi thứ ba, cụ thể, ≤1024 ký tự. Ví dụ / example — "Analyzes X and reports Y. Use when the user has Z. Triggers on <từ khoá song ngữ>".
license: MIT
# --- Trường tuỳ chọn theo Agent Skills spec (agentskills.io/specification) ---
# compatibility: Requires Python 3.10+ and pandas   # chỉ thêm khi skill có yêu cầu môi trường (≤500 ký tự)
# metadata:                                          # map chuỗi→chuỗi cho dữ liệu ngoài spec
#   author: your-name
#   version: "1.0"
#   status: scaffold                                 # đánh dấu skill chưa hoàn thiện (KHÔNG dùng key top-level 'status')
# allowed-tools: Read Bash                           # thử nghiệm: danh sách công cụ tách bằng dấu cách
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
- `references/` — ghi chú/tài liệu tham khảo (Claude nạp khi cần).
- `assets/` — dữ liệu mẫu, template để test.

## Ghi chú / Notes
- Chỉ có `name` + `description` là bắt buộc; các trường còn lại tuỳ chọn.
- Giữ `SKILL.md` gọn (< 500 dòng) — tách chi tiết dài sang `references/`.
- Không đưa lệnh nguy hiểm, gọi mạng ngoài, hay đọc secret vào skill.
- Chạy `python scripts/validate_skill.py` và `python scripts/audit_skill.py`
  trỏ vào thư mục skill (+ `validate_marketplace.py`) trước khi mở PR.
