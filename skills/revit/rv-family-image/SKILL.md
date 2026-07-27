---
name: rv-family-image
description: >
  Creates a Revit Family (.rfa) from a reference image of ANY furniture,
  fixture, or architectural element using the T3Lab_Lite JSONtoFamily tool
  via MCP Revit connector. Trigger whenever the user uploads a photo, sketch,
  or reference image and wants to generate a Revit Family automatically.
  Triggers: "tạo family từ ảnh", "create family from image", "generate revit
  family", "json to family", "t3lab", "family từ hình", "tạo family revit",
  or any combination of "image/ảnh + revit/family/rfa".
license: MIT
compatibility: Requires a Revit MCP connector exposing the T3Lab_Lite JSONtoFamily tool; generates a family from an analyzed image. Needs a concrete input image to run.
metadata:
  software: revit
  discipline: multi
  category: automation
---

# Revit Family from Image

Analyze ANY furniture/fixture image → generate Family JSON → execute in Revit via MCP.

---

## Architecture

```
User: image + "tạo family"
         │
         ▼
[Stage 0] Check Family Document
   ├─ YES → tiếp tục
   └─ NO  → hỏi loại family → tự mở .rft template qua MCP
         │
         ▼
[Stage 1] Đọc t3lab-prompt.md
         │
         ▼
[Stage 2] Phân tích ảnh → generate + validate JSON → preview → confirm
         │
         ▼
[Stage 3] execute_revit_code → generate_family_from_json(dict)
         │
         ▼
[Stage 4] Hỏi tên file → build filename → Save As .rfa qua MCP
```

---

## Stage 0 — Check & Open Family Document

### 0a — Kiểm tra trạng thái

```python
if doc.IsFamilyDocument:
    print("OK|" + doc.Title)
else:
    print("NOT_FAMILY|" + doc.Title)
```

### 0b — Nếu KHÔNG phải Family Document

Hỏi user bằng câu hỏi có lựa chọn, dựa trên object type đã detect từ ảnh:

Ví dụ nếu ảnh là sofa:
> "Mình cần mở một Family Template để tạo family. Dựa trên ảnh (sofa/ghế),
> template phù hợp nhất là **Metric Furniture**. Bạn confirm không, hay muốn
> chọn loại khác?"
>
> A) Metric Furniture ← recommended
> B) Metric Casework
> C) Metric Generic Model
> D) Chọn khác (gõ tên)

### 0c — Map object type → recommended template

| Object type | Recommended template |
|---|---|
| Sofa, armchair, chair, table, bed, shelf | `Metric Furniture.rft` |
| Kitchen cabinet, wardrobe, casework | `Metric Casework.rft` |
| Sink, toilet, bathtub, lavatory | `Metric Plumbing Fixture.rft` |
| Wall-mounted sink/fixture | `Metric Plumbing Fixture wall based.rft` |
| Pendant lamp, floor lamp | `Metric Lighting Fixture.rft` |
| Ceiling lamp | `Metric Lighting Fixture ceiling based.rft` |
| Wall sconce | `Metric Lighting Fixture wall based.rft` |
| Spot light ceiling | `Metric Spot Lighting Fixture ceiling based.rft` |
| Mechanical equipment | `Metric Mechanical Equipment.rft` |
| Electrical equipment | `Metric Electrical Equipment.rft` |
| Decorative / generic | `Metric Generic Model.rft` |
| Specialty equipment | `Metric Specialty Equipment.rft` |
| Plant, entourage | `Metric Entourage.rft` |

### 0d — Mở template qua MCP

Sau khi user confirm template:

```python
import os
template_path = r"C:\ProgramData\Autodesk\RVT 2026\Family Templates\English\{TEMPLATE_NAME}"

app = doc.Application
new_family_doc = app.NewFamilyDocument(template_path)
print("OPENED|" + new_family_doc.Title)
```

Sau khi mở → **tiếp tục Stage 1** với document mới.

---

## Stage 1 — Schema

Luôn đọc `references/t3lab-prompt.md` trước. Không hỏi user về schema.

---

## Stage 2 — Analyze: Image → Family JSON

### 2a — Pre-analysis

| Property | How |
|---|---|
| **Object type** | sofa, armchair, chair, sink, lamp, table, bed, wardrobe... |
| **family_name** | English PascalCase_Underscore (dùng tạm, sẽ rename ở Stage 4) |
| **Category** | Xem `references/category-map.md` |
| **Overall dims** | W × D × H mm. Hỏi nếu không rõ. |
| **Components** | Phân tách: seat/back/legs/arms/frame/basin/shade... |
| **Geometry type** | Extrusion / Sweep / Revolve / Blend / SweptBlend per part |
| **Materials** | Fabric/wood/metal/ceramic → `material_param` |

Nếu thiếu dimension → hỏi **đúng 1 câu**. Dùng defaults cho phần còn lại.

### 2b — JSON Rules (từ t3lab-prompt.md + source code)

1. Root: `family_name`, `parameters`, `reference_planes`, `dimensions`, `geometry`
2. Units: **mm** (script auto-convert với SCL = 1/304.8)
3. Parameter types: `"Length"`, `"Material"`, `"YesNo"` only
4. Profile loops phải **continuous** (p2[N] = p1[N+1])
5. `profile_2d` cho Sweep → Z=0 tất cả points
6. Blend → `bottom_profile` và `top_profile` phải có **cùng số segments**
7. SweptBlend → path chỉ dùng segment đầu tiên
8. Voids: `"is_solid": false` + `"cuts": ["solid_id"]`
9. Minimum parameters: `Width`, `Depth`, `Height`

### 2c — Validation

- [ ] Profile loops continuous
- [ ] Blend: equal segment count
- [ ] Sweep profile_2d: Z=0
- [ ] Geometry IDs: unique
- [ ] Dimension planes: khớp reference_planes names
- [ ] JSON syntax valid

### 2d — Preview + Confirm

```
📦 Family:     [FamilyName]
📐 Category:   [Category]
🔢 Parameters: Width=[x], Depth=[y], Height=[z]
🧱 Geometry:   [N] parts
   ├─ [id]  [Type]  [dims]
📏 Overall:    W[x] × D[y] × H[z] mm
```

Hỏi: **"Confirm để tạo family trong Revit?"**

---

## Stage 3 — Execute via MCP

### 3a — Chạy generate_family_from_json

```python
import sys
sys.path.append(r"D:\code_revit\revit-API_t3lab-lite\T3Lab_Lite.extension\T3Lab_Lite.tab\Project.panel\FamilyWork.stack\JSONtoFamily.pushbutton")

import script as t3lab_script
t3lab_script.doc = doc

family_dict = { ...ACTUAL DICT... }  # Python dict, không phải JSON string

try:
    t3lab_script.generate_family_from_json(family_dict)
    print("SUCCESS")
except Exception as e:
    print("ERROR: " + str(e))
```

### 3b — Fallback nếu import thất bại

Copy trực tiếp các functions: `SCL`, `to_xyz`, `to_vec`, `to_xyz_2d`,
`project_to_plane`, `create_curve_from_json`, `build_sweep_profile`,
`get_model_text_type`, `generate_family_from_json`.
Bỏ qua tất cả UI imports (WPF, forms).

### 3c — Errors thường gặp

| Error | Fix |
|---|---|
| Import error (WPF) | Dùng fallback |
| Profile not closed | Fix loop continuity |
| Blend segment mismatch | Equalize count |
| NewDimension failed | Non-fatal, tiếp tục |

---

## Stage 4 — Naming & Save As

### 4a — Hỏi tên file

Sau khi generate thành công, hỏi user:

> "Family đã được tạo! Bây giờ mình cần đặt tên file để save.
> Cấu trúc tên: **ARC_[Category]_[Brand]_[Name]**
>
> Ví dụ: `ARC_Furniture_Knoll_BarcelonaSofa`
>
> - **Category** = loại family (Furniture / Plumbing / Lighting / Casework...)
> - **Brand** = thương hiệu / nhà sản xuất (nếu không có gõ 'Generic')
> - **Name** = tên sản phẩm cụ thể
>
> Brand của sản phẩm trong ảnh là gì? Và tên sản phẩm là gì?"

### 4b — Build filename

Từ thông tin user cung cấp:

```
filename = "ARC_{Category}_{Brand}_{Name}.rfa"
```

Rules:
- Không có dấu cách → dùng PascalCase hoặc underscore
- Không có ký tự đặc biệt: `/ \ : * ? " < > |`
- Category tự động từ template đã chọn ở Stage 0:
  - Furniture → `Furniture`
  - Plumbing Fixture → `Plumbing`
  - Lighting Fixture → `Lighting`
  - Casework → `Casework`
  - Generic Model → `Generic`
  - Specialty Equipment → `Specialty`

Ví dụ confirm với user:
> "Tên file sẽ là: **ARC_Furniture_Knoll_BarcelonaSofa.rfa**
> Lưu vào đâu? (default: Desktop)"

### 4c — Save As qua MCP

```python
import os

save_folder = r"C:\Users\trant\Desktop"  # hoặc path user chỉ định
filename = "ARC_Furniture_Knoll_BarcelonaSofa.rfa"
full_path = os.path.join(save_folder, filename)

save_options = SaveAsOptions()
save_options.OverwriteExistingFile = True

doc.SaveAs(full_path, save_options)
print("SAVED|" + full_path)
```

### 4d — Confirm save

```
✅ Family đã được lưu:
📁 ARC_Furniture_Knoll_BarcelonaSofa.rfa
📂 C:\Users\trant\Desktop\ARC_Furniture_Knoll_BarcelonaSofa.rfa
```

---

## Naming Convention Reference

```
ARC _ [Category] _ [Brand] _ [Name]
 │         │           │         │
 │         │           │         └─ Tên sản phẩm (PascalCase)
 │         │           └─────────── Thương hiệu / nhà SX
 │         └─────────────────────── Loại family Revit
 └───────────────────────────────── Prefix dự án (cố định)
```

Ví dụ thực tế:
- `ARC_Furniture_Herman_EamesLounge`
- `ARC_Furniture_Generic_ArmchairFabric`
- `ARC_Plumbing_Kohler_UndermountSink`
- `ARC_Lighting_Flos_ArcFloorLamp`
- `ARC_Casework_Generic_KitchenUpperCabinet`

---

## Template Path (confirmed)

```
C:\ProgramData\Autodesk\RVT 2026\Family Templates\English\
```

Key templates:
- `Metric Furniture.rft`
- `Metric Casework.rft` / `Metric Casework wall based.rft`
- `Metric Plumbing Fixture.rft` / `Metric Plumbing Fixture wall based.rft`
- `Metric Lighting Fixture.rft` / `ceiling based` / `wall based`
- `Metric Generic Model.rft`
- `Metric Specialty Equipment.rft`
- `Metric Mechanical Equipment.rft`

---

## Reference Files

- **`references/t3lab-prompt.md`** ← ĐỌC TRƯỚC — schema + rules + examples
- **`references/script-api.md`** — API đầy đủ của script.py
- **`references/category-map.md`** — Object → Revit category + default dims
