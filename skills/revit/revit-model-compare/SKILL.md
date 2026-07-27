---
name: revit-model-compare
description: Compares two Revit element exports (old vs new snapshot) keyed by Element ID or GUID and reports what was added, deleted, or changed — including which fields changed from what to what — with an optional diff CSV. Use when QA-ing changes between two model versions or coordination rounds, or reviewing what moved between issues. Triggers on "model compare", "model diff", "what changed", "compare versions", "element diff", "so sánh model", "kiểm tra thay đổi model".
license: MIT
metadata:
  software: revit
  discipline: multi
  category: qa
---

# Model Compare — So sánh hai phiên bản model

Ghép hai bản export element (Element ID/GUID) và báo cáo **thêm mới / xoá / thay
đổi** giữa hai phiên bản model — kèm trường nào đổi từ gì → gì, và (tuỳ chọn)
diff CSV.
Diff two element exports keyed by Element ID/GUID; reports added / deleted /
changed with field-level detail and an optional diff CSV.

## Khi nào dùng / When to use
- QA thay đổi giữa hai lần phát hành model, hoặc giữa hai vòng coordination.
- Cần biết chính xác element nào mới, nào bị xoá, nào đổi type/level/tham số.

## Cách dùng / How to use
```bash
python scripts/compare_models.py <old.csv> <new.csv>
# chỉ so sánh vài cột + ghi diff CSV:
python scripts/compare_models.py <old.csv> <new.csv> --compare-cols Type,Level --csv out/diff.csv
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/compare_models.py assets/sample_model_v1.csv assets/sample_model_v2.csv
```

## Đầu ra / Output
- Tóm tắt: số element cũ/mới, **Added / Deleted / Changed** (kèm phân bố theo category).
- Danh sách element thêm/xoá; với **changed** liệt kê từng trường `old → new`.
- (Tuỳ chọn) CSV diff: `id, change, field, old, new`.

## Ghi chú / Notes
- Chỉ dùng thư viện chuẩn (`csv`).
- Tự dò cột ID theo alias (Element ID / GUID / Unique ID…); ép bằng `--id-col`.
- Mặc định so sánh mọi cột chung (trừ ID); giới hạn bằng `--compare-cols`.
- Export từ Revit bằng schedule (thêm cột **Element ID**) hoặc Dynamo/pyRevit
  (`element.Id` / `UniqueId`) cho cả hai phiên bản với cùng bộ cột.
