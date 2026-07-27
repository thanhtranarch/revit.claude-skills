---
name: pdf-markup-compare
description: Compare two revisions of a PDF drawing/document and report what changed — added, removed, and moved annotations/markups (text notes, clouds, comments), plus per-page text differences. Use when the user has two PDF versions (e.g. Rev A vs Rev B, or a marked-up set vs a clean set) and asks what changed, to diff markups, compare comments, or track revisions. Triggers on "compare PDF", "so sánh PDF", "markup diff", "so sánh markup", "what changed between revisions", "Bluebeam markup".
---

# PDF Markup Compare — So sánh markup giữa 2 bản PDF

So sánh hai phiên bản PDF và liệt kê thay đổi: annotation/markup được **thêm,
xoá, di chuyển**, cùng khác biệt text theo từng trang.
Compare two PDF revisions and report added / removed / moved annotations plus
per-page text differences.

## Khi nào dùng / When to use
- Có 2 bản PDF (vd Rev A vs Rev B, hoặc bản có markup vs bản sạch).
- Cần biết đã thêm/bớt comment, cloud, ghi chú gì; hoặc nội dung text đổi ở đâu.

## Cách làm / How to use
```bash
python scripts/compare_markup.py <old.pdf> <new.pdf>
# xuất CSV danh sách thay đổi markup:
python scripts/compare_markup.py <old.pdf> <new.pdf> --csv out/markup_diff.csv
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/compare_markup.py assets/rev_a.pdf assets/rev_b.pdf
```

## Nó so sánh gì / What it compares
1. **Annotation/markup** (lấy từ `/Annots`): loại (Text, FreeText, Square,
   Polygon/cloud, Highlight…), nội dung, trang, toạ độ. Ghép cặp theo nội dung
   + vị trí gần nhau để phân biệt *added / removed / moved*.
2. **Text từng trang**: diff theo dòng để chỉ ra nội dung thêm/bớt.

## Đầu ra / Output
- Tóm tắt theo trang: số markup thêm / xoá / di chuyển.
- (Tuỳ chọn) CSV: mỗi dòng một thay đổi (change_type, page, subtype, content,
  vị trí) để đưa vào biên bản review.

## Ghi chú / Notes & giới hạn
- Cần `pypdf` (xem `requirements.txt`).
- Đọc annotation ở tầng cấu trúc PDF, **không** so sánh pixel/hình ảnh. Markup
  "flatten" vào nội dung trang sẽ không còn là annotation → chỉ hiện ở diff text.
- PDF quét (scan) không có annotation → dùng skill OCR trước nếu cần.
