---
name: shared-coordinates
description: Provides guidance and a verification checklist for setting up and QA-ing shared coordinates across a multi-model BIM project — survey point, project base point, true north vs project north, and acquire/publish coordinates between host and linked models. Use when the user is setting up coordinates, links do not line up, models appear offset or rotated, or they ask how to acquire/publish coordinates. Triggers on "shared coordinates", "survey point", "project base point", "acquire coordinates", "models not aligned", "toạ độ chung", "coordinate setup".
license: MIT
---

# Shared Coordinates — Thiết lập & kiểm tra toạ độ chung

Hướng dẫn + checklist thiết lập và QA toạ độ chung cho dự án nhiều model
(host + link): survey point, project base point, true/project north,
acquire/publish coordinates.

## Khi nào dùng / When to use
- Bắt đầu set up coordinate cho dự án, hoặc link bị lệch/xoay/không khớp.

## Khái niệm cốt lõi / core concepts
- **Survey Point (SP):** điểm khảo sát thực địa — gốc toạ độ *shared/real world*.
- **Project Base Point (PBP):** gốc làm việc nội bộ của model.
- **Internal Origin:** gốc phần mềm (không nên đưa mô hình đi quá xa gốc này —
  >~20 miles/32 km gây lỗi độ chính xác).
- **Acquire Coordinates:** model nhận toạ độ *từ* một link (link là "chủ" toạ độ).
- **Publish Coordinates:** đẩy toạ độ *ra* một link (host là "chủ").

## Checklist thiết lập / setup checklist
1. Chọn **một model chủ toạ độ** duy nhất (thường là kiến trúc hoặc site).
2. Đặt SP theo mốc khảo sát thật; ghi lại E/N/Elev + góc true north.
3. Các model khác **Acquire Coordinates** từ model chủ (không tự đặt tay).
4. Link bằng **Auto – By Shared Coordinates** (không dùng Origin to Origin nếu
   đã thống nhất shared coords).
5. Khoá SP/PBP (ổ khoá) sau khi set để tránh xê dịch vô ý.
6. Thống nhất **project north** (hướng vẽ) vs **true north** (hướng thật).

## Checklist QA khi lệch / troubleshooting
- Link lệch/nhảy vị trí → kiểm tra link đang dùng *By Shared Coordinates* hay
  *Origin to Origin*; kiểm tra model đã Acquire đúng chủ chưa.
- Xoay khác nhau → true north/project north không đồng bộ giữa các model.
- Lệch cao độ → kiểm tra Elevation của SP và Project Elevation vs Survey.
- Mô hình quá xa internal origin → cảnh báo độ chính xác, kéo gần lại.

## Kiểm tự động / auto-check
Export toạ độ Survey Point + góc true north của từng model ra CSV (model, sp_e,
sp_n, sp_elev, angle, reference) rồi so với model chủ theo dung sai:
```bash
python scripts/check_coordinates.py <coords.csv> --reference AR --tol 1.0 --angle-tol 0.01
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/check_coordinates.py assets/sample_coordinates.csv
```
Báo `OK / OFFSET (ΔE/ΔN/ΔElev) / ROTATED (Δangle)` cho từng model; exit 1 nếu có
lệch (dùng làm gate trước federate/clash).

## Ghi chú / Notes
- Script chỉ dùng thư viện chuẩn (`csv`); dung sai theo đơn vị dữ liệu (thường mm).
- Kết hợp: `shared-coordinates` (toạ độ khớp) → `model-federation` (gộp) →
  `clash-report-analysis` (check clash có nghĩa).
