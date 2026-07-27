# T3Lab_Lite JSONtoFamily — Confirmed API (từ script.py)

## Script location
```
D:\code_revit\revit-API_t3lab-lite\T3Lab_Lite.extension\T3Lab_Lite.tab\
  Project.panel\FamilyWork.stack\JSONtoFamily.pushbutton\script.py
```

## Key function
```python
generate_family_from_json(schema: dict)
```
- Nhận một Python dict (đã parse từ JSON)
- Wrap trong `revit.Transaction("Generate Parametric Family from JSON")`
- Dùng `doc` global từ pyRevit context

## Metric conversion
```python
IS_METRIC = True
SCL = 1.0 / 304.8   # mm → feet
```
→ **Tất cả values trong JSON phải là mm**

## Requirements
- `doc.IsFamilyDocument` phải là `True`
- Family template phải có ít nhất 1 Plan view + 1 Front Elevation view
- Nếu không có `CurrentType`, script tự tạo type "Standard"

## Geometry types supported (confirmed)
Extrusion, Sweep, Revolve, Blend, SweptBlend, ModelText, Void

## How to call via MCP
```python
import sys, json, importlib

SCRIPT_DIR = r"D:\code_revit\revit-API_t3lab-lite\T3Lab_Lite.extension\T3Lab_Lite.tab\Project.panel\FamilyWork.stack\JSONtoFamily.pushbutton"
sys.path.insert(0, SCRIPT_DIR)
m = importlib.import_module("script")
m.generate_family_from_json(json.loads(json_string))
```

## What the function does internally (step by step)
1. Find Plan view + Elevation view in doc
2. Create FamilyManager types if none exist
3. Add parameters (Length / Material / YesNo)
4. Create reference planes
5. Create dimensions + bind to parameters
6. Create geometry (Extrusion/Sweep/Revolve/Blend/SweptBlend/ModelText)
7. Bind material_param and visible_param to family parameters
8. Lock faces to reference planes (alignments)
9. Apply void cuts (CombineElements)

## Notes on edge cases
- SweptBlend: chỉ dùng path segment đầu tiên
- Alignment failures: silent warning, geometry vẫn được tạo
- inner_loops trong Extrusion: hỗ trợ holes bên trong profile
- ModelText: cần ModelTextType đã tồn tại trong template
