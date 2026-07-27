---
name: rv-spellcheck-review
description: Spell-checks English text exported from a Revit model — sheet names, view names, room/space names, keynotes, text notes, and schedule text — flagging common misspellings, repeated words, and placeholder/junk text (TBD, TBC, XXX, ???, "do not use"), with an optional dictionary mode that also finds unknown words while ignoring AEC/Revit jargon via a glossary allowlist. Use when QA-ing sheet and view names before a drawing issue, proofreading keynotes and annotation text, or catching leftover placeholders in a Revit text export. Triggers on "spellcheck", "spell check", "typos", "proofread sheet names", "keynote typos", "placeholder text", "TBD", "check spelling in Revit", "soát chính tả Revit", "kiểm tra lỗi chính tả tên sheet".
license: MIT
metadata:
  software: revit
  discipline: multi
  category: standards
---

# Revit Spellcheck Review — Soát lỗi chính tả text trong Revit

Soát lỗi chính tả (tiếng Anh) cho text export từ Revit: **tên sheet**, **tên
view**, **tên phòng/space**, **keynote**, **text note**, **text trong schedule**.
Bắt **lỗi thường gặp**, **từ lặp**, và **chữ giữ chỗ** (TBD/TBC/XXX/???/DO NOT
USE); chế độ nâng cao còn dò **từ lạ** nhưng bỏ qua thuật ngữ chuyên ngành theo
glossary.
Spell-checks English text exported from a Revit model, ignoring domain jargon.

## Khi nào dùng / When to use
- Soát **tên sheet / tên view** trước khi phát hành bộ bản vẽ.
- Proofread **keynote / text note / general note** trong model.
- Bắt **chữ giữ chỗ** còn sót (TBD, XXX, "to be confirmed") trước issue.

## Cách dùng / How to use
Export text cần soát ra CSV (vd cột `Text`) — từ schedule sheet list, keynote
legend, room schedule, hoặc copy text note. Rồi:
```bash
# Chế độ mặc định (không cần cài gì): lỗi thường gặp + từ lặp + chữ giữ chỗ
python scripts/spellcheck.py <export.csv> --col Text
python scripts/spellcheck.py <notes.txt>

# Chế độ đầy đủ (thêm phát hiện "từ lạ") — cần pyspellchecker:
python scripts/spellcheck.py <export.csv> --col Text --dict
```
Thử nhanh với mẫu / quick test:
```bash
python scripts/spellcheck.py assets/sample_text.csv --col Text
```

## Hai chế độ / two modes
- **Mặc định** — chỉ dùng thư viện chuẩn. Bảng lỗi thường gặp
  (`clearence→clearance`, `schedual→schedule`, `dimention→dimension`…) + từ lặp
  ("the the") + **chữ giữ chỗ** (TBD/TBC/XXX/???/"do not use" — tắt bằng
  `--no-placeholder`). Độ chính xác cao, gần như không báo nhầm.
- **`--dict`** — nếu có `pyspellchecker`, bổ sung dò **từ lạ** và gợi ý sửa; loại
  trừ jargon AEC/Revit bằng `references/aec-glossary.txt` (MEP, HVAC, RFI,
  titleblock, keynote, mullion…). Acronym viết hoa & từ có số được bỏ qua.

## Tuỳ biến / customize
- Thêm từ vào `references/aec-glossary.txt` (mỗi dòng một từ) để giảm báo nhầm
  với tên riêng, mã sản phẩm, tên bộ môn của dự án.
- Bổ sung lỗi hay gặp vào `COMMON_MISSPELLINGS` trong script.

## Đầu ra / Output
- Danh sách phát hiện: loại (PLACEHOLDER/MISSPELLING/REPEATED/UNKNOWN) · vị trí
  (row/line) · từ · gợi ý. Exit ≠ 0 nếu có phát hiện (tiện QA/CI gate).

## Ghi chú / Notes
- Chỉ tiếng Anh. Text tiếng Việt nên soát bằng công cụ khác.
- Bổ trợ `rv-sheet-naming` (kiểm **pattern** số/tên sheet) — skill này soát
  **chính tả** nội dung text.
- Chế độ `--dict` có thể báo nhầm với tên riêng/sản phẩm — thêm vào glossary.
