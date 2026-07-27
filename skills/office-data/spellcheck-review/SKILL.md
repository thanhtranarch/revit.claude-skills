---
name: spellcheck-review
description: Spell-checks English text pulled from AEC documents and registers — sheet names, drawing notes, RFI/comment logs, specifications, schedule text — flagging common misspellings, repeated words, and placeholder/junk text (TBD, TBC, XXX, ???, "do not use"), with an optional dictionary mode that also finds unknown words while ignoring AEC jargon via a glossary allowlist. Use when reviewing document text for typos or leftover placeholders before issue, checking a comment/RFI register, or QA-ing sheet names. Triggers on "spellcheck", "spell check", "typos", "proofread", "placeholder text", "TBD", "check spelling", "soát chính tả", "kiểm tra lỗi chính tả", "review typo".
license: MIT
metadata:
  software: office-data
  discipline: multi
  category: standards
---

# Spellcheck Review — Soát lỗi chính tả tài liệu AEC

Soát lỗi chính tả (tiếng Anh) cho text lấy từ tài liệu/register AEC: tên sheet,
ghi chú bản vẽ, log RFI/comment, spec, text schedule. Bắt **lỗi thường gặp**,
**từ lặp**, và **chữ giữ chỗ** (TBD/TBC/XXX/???/DO NOT USE); chế độ nâng cao còn
tìm **từ lạ** nhưng bỏ qua thuật ngữ chuyên ngành theo glossary.
Spell-check English text from AEC documents, ignoring domain jargon.

## Khi nào dùng / When to use
- Soát typo trước khi phát hành (drawing notes, spec, comment log).
- QA tên sheet / tên view / register comment.

## Cách dùng / How to use
```bash
# Chế độ mặc định (không cần cài gì): lỗi thường gặp + từ lặp
python scripts/spellcheck.py <text.txt>
python scripts/spellcheck.py <register.csv> --col Comment

# Chế độ đầy đủ (thêm phát hiện "từ lạ") — cần pyspellchecker:
python scripts/spellcheck.py <register.csv> --col Comment --dict
```
Thử nhanh với mẫu / quick test:
```bash
python scripts/spellcheck.py assets/sample_text.csv --col Comment
```

## Hai chế độ / two modes
- **Mặc định** — chỉ dùng thư viện chuẩn. Bảng lỗi thường gặp
  (`clearence→clearance`, `schedual→schedule`…) + từ lặp ("the the") + **chữ giữ
  chỗ** (TBD/TBC/XXX/???/"do not use" — tắt bằng `--no-placeholder`).
  Độ chính xác cao, gần như không báo nhầm.
- **`--dict`** — nếu có `pyspellchecker`, bổ sung dò **từ lạ** (unknown word) và
  gợi ý sửa; loại trừ jargon AEC bằng `references/aec-glossary.txt` (MEP, HVAC,
  RFI, sprinkler, curtainwall…). Acronym viết hoa & từ có số cũng được bỏ qua.

## Tuỳ biến / customize
- Thêm từ vào `references/aec-glossary.txt` (mỗi dòng một từ) để giảm báo nhầm.
- Bổ sung lỗi hay gặp vào `COMMON_MISSPELLINGS` trong script.

## Đầu ra / Output
- Danh sách phát hiện: loại (PLACEHOLDER/MISSPELLING/REPEATED/UNKNOWN) · vị trí
  (row/line) · từ · gợi ý. Exit ≠ 0 nếu có phát hiện (tiện QA/CI).

## Ghi chú / Notes
- Chỉ tiếng Anh. Text tiếng Việt nên soát bằng công cụ khác.
- Chế độ `--dict` có thể báo nhầm với tên riêng/sản phẩm — thêm vào glossary.
