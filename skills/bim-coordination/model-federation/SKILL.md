---
name: model-federation
description: Federate multiple discipline models into a single coordination model (Navisworks NWF/NWD or ACC Model Coordination) — append order, file naming, refresh workflow, and a clash-readiness check of units, coordinates, and model freshness before running clash. Use when combining discipline models for coordination or preparing a federated model. Triggers on "federate models", "NWF", "append models", "coordination model", "model federation", "gộp model".
---

# Model Federation — Gộp model coordination

Hướng dẫn + checklist gộp nhiều model bộ môn thành một model coordination
(Navisworks NWF/NWD hoặc ACC Model Coordination), kèm **script kiểm tra sẵn sàng
clash** (đơn vị, hệ toạ độ, model cũ).
Guidance + checklist to federate discipline models, plus a clash-readiness
checker for units, coordinates, and freshness.

## Khi nào dùng / When to use
- Gộp model nhiều bộ môn để coordination / chuẩn bị model federated trước clash.
- Kiểm nhanh danh sách model đã "đồng nhất" chưa trước khi chạy clash.

## Cách dùng / How to use
1. **Theo checklist** trong `references/federation-checklist.md` (append order,
   naming, refresh, readiness).
2. **Kiểm tự động** danh sách model (CSV: file, discipline, coord_system, units,
   last_updated) để bắt lệch đơn vị/toạ độ và model cũ:
   ```bash
   python scripts/check_model_list.py <models.csv> --as-of 2026-07-24 --stale-days 7
   ```
   Thử nhanh với dữ liệu mẫu / quick test:
   ```bash
   python scripts/check_model_list.py assets/sample_model_list.csv --as-of 2026-07-24
   ```

## Nguyên tắc cốt lõi / core principles
- **Một nguồn toạ độ**: mọi model dùng chung shared coordinates (xem skill
  `shared-coordinates`). Đơn vị thống nhất (thường mm).
- **Host federation**: NWF (Navisworks) *tham chiếu* file bộ môn → refresh được;
  NWD là ảnh chụp *đóng băng* để phát hành/lưu vết.
- **Thứ tự append** theo bộ môn, tên file nhất quán, selection sets/search sets
  để lọc clash có nghĩa.

## Đầu ra / Output
- Checklist federate theo bước; verdict **READY / NOT READY** từ script
  (🔴 lệch đơn vị/toạ độ, thiếu toạ độ; 🟡 model cũ, thiếu thông tin). Exit 1 nếu
  NOT READY (dùng làm gate trước clash).

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`, `datetime`).
- Kết hợp: `shared-coordinates` (toạ độ khớp) → `model-federation` (gộp) →
  `clash-report-analysis` (đọc kết quả clash) → `coordination-issue-log` (giao việc).
