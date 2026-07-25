---
name: risk-register
description: Score and rate a project risk register from a CSV — convert probability and impact (1-5 or Low/Medium/High) into a P×I score, assign RAG (red/amber/green), roll up by RAG, owner, and category, flag overdue reviews, and list the top open risks. Use when maintaining a risk register or producing a risk summary for a report or review meeting. Triggers on "risk register", "risk matrix", "probability impact", "RAG rating", "top risks", "đăng ký rủi ro", "ma trận rủi ro".
---

# Risk Register — Chấm điểm & phân loại rủi ro

Chấm điểm risk register: đổi **probability × impact** (1–5 hoặc Low/Medium/High)
thành điểm P×I, gán **RAG** (đỏ/vàng/xanh), gom theo RAG/owner/category, bắt
**review quá hạn**, và liệt kê **top rủi ro** đang mở.
Score a risk register (P×I → RAG), roll up by RAG/owner/category, flag overdue
reviews, and list the top open risks.

## Khi nào dùng / When to use
- Có risk register (CSV) cần cập nhật điểm & RAG, chuẩn bị báo cáo/họp review.
- Cần biết rủi ro đỏ, ai làm chủ, nhóm nào nhiều, review nào trễ.

## Cách dùng / How to use
```bash
python scripts/score_risks.py <risks.csv>
python scripts/score_risks.py <risks.csv> --as-of 2026-07-24 --csv out/risk_register.csv
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/score_risks.py assets/sample_risks.csv --as-of 2026-07-24
```

## Thang điểm / scoring
- `probability`, `impact`: **1–5** hoặc chữ (Very Low…Very High / Unlikely…Almost
  Certain / Minor…Critical). Điểm = P × I (1–25).
- **RAG**: `RED` ≥ 15 · `AMBER` 8–14 · `GREEN` < 8.

## Đầu ra / Output
- Tổng / open / closed; đếm theo **RAG**, **owner**, **category** (rủi ro đang mở).
- Danh sách **review quá hạn**; **top 5 rủi ro** đang mở (điểm cao nhất).
- (Tuỳ chọn) CSV register + cột `score`, `rag`, `review_overdue`.

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `datetime`).
- Đóng / closed: status ∈ {closed, retired, expired, realised}. Chỉ rủi ro đang
  mở mới tính review quá hạn.
- Tự dò cột theo alias (xem `references/risk-columns.md`).
