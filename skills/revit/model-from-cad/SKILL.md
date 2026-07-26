---
name: model-from-cad
description: Kick-starts building a Revit model from an imported CAD drawing — parses an ASCII DXF to inventory layers and entities (lines, polylines, blocks, text), total lengths, and a bounding box, then emits a build-plan JSON (line segments and block insertion points per layer) that the bundled pyRevit and Dynamo templates consume to create walls from lines and columns from blocks. Use when converting a 2D CAD plan into model elements or auditing a CAD import before modelling. Triggers on "model from CAD", "walls from CAD", "columns from CAD", "DXF to Revit", "build model from drawing", "dựng model từ CAD", "tạo tường từ CAD", "dựng model từ hình vẽ".
license: MIT
metadata:
  software: revit
  discipline: multi
  category: automation
---

# Model from CAD — Dựng model Revit từ hình vẽ (DXF)

Tăng tốc "dựng model từ hình vẽ": đọc **DXF (ASCII)**, kiểm kê layer/đối tượng
(line, polyline, block, text), tính tổng chiều dài & bounding box, rồi xuất
**build plan JSON** (segments + points theo layer). Template pyRevit/Dynamo dùng
plan này để tạo **tường từ line** và **cột từ block**.
Parse a DXF, emit a build plan, and feed it to pyRevit/Dynamo templates that
create walls from lines and columns from blocks.

## Khi nào dùng / When to use
- Có bản CAD (plan) cần dựng nhanh khung model Revit (tường/cột/grid).
- Cần kiểm kê CAD import trước khi mô hình hoá (layer nào, bao nhiêu line/block).

## Cách dùng / How to use
```bash
# 1) Kiểm kê CAD + xem gợi ý phần tử theo layer:
python scripts/parse_dxf.py <plan.dxf>
# 2) Xuất build plan JSON cho template pyRevit/Dynamo:
python scripts/parse_dxf.py <plan.dxf> --json > plan.json
```
Thử nhanh với dữ liệu mẫu / quick test:
```bash
python scripts/parse_dxf.py assets/sample_plan.dxf
```
Rồi trong Revit: chạy `templates/pyrevit_walls_from_lines.py` (pyRevit) và
`templates/dynamo_columns_from_points.py` (Dynamo). Xem
`references/cad-to-model-workflow.md`.

## Đầu ra / Output
- Bảng: mỗi layer → số line/poly/circle/insert/text, tổng chiều dài, **gợi ý phần
  tử** (Wall/Column/Beam/Grid…). Bounding box toàn bản vẽ.
- `--json`: build plan gồm `segments` (line) và `points` (block) từng layer để
  template tạo phần tử; đổi mm→ft trong template.

## Ghi chú / Notes
- Script chỉ dùng thư viện chuẩn (`json`, `math`); chỉ đọc **DXF ASCII** (DWG/DXF
  nhị phân cần convert trước).
- Template chạy **trong Revit** (không phải CLI của repo), dùng Transaction, không
  đọc secret / gọi mạng. Duyệt kết quả và QA bằng `revit-warnings-audit` /
  `revit-model-audit` sau khi dựng.
