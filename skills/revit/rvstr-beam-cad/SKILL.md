---
name: rvstr-beam-cad
description: >
  Tự động tạo Structural Beam trong Revit từ file CAD đã import, dựa trên layer chứa đường beam.
  Bao gồm: tìm file CAD theo tầng, đọc layer beam, ghép cặp đường song song thành centerline,
  tạo beam type nếu chưa có, và đặt beam với z-offset đúng theo yêu cầu.

  LUÔN dùng skill này khi user yêu cầu:
  - "vẽ beam từ CAD", "tạo beam từ file cad", "draw beams from CAD"
  - "dựng beam tầng X", "model beams level X"
  - "tạo type beam", "add beam types", "thêm type dầm"
  - Bất kỳ yêu cầu nào kết hợp "beam/dầm" + "CAD/DWG" + "Revit/tầng/level"
  - Yêu cầu tạo beam với offset âm xuống (z-offset)
license: MIT
compatibility: Requires Revit + pyRevit/IronPython MCP connector; reads an imported CAD link and creates structural framing (beams) inside a Transaction. Confirm level, type mapping and z-offset with the user before writing.
metadata:
  software: revit
  discipline: structural
  category: automation
---

# Revit Beam From CAD — Skill

Workflow tự động tạo Structural Beam trong Revit bằng cách đọc geometry từ layer beam của file CAD đã import.

---

## WORKFLOW TỔNG QUAN

```
1. KIỂM TRA KẾT NỐI  →  2. TÌM CAD FILE  →  3. ĐỌC LAYER BEAM
         ↓
4. GHÉP CẶP ĐƯỜNG   →  5. XÁC ĐỊNH TYPE  →  6. TẠO BEAM TYPE (nếu chưa có)
         ↓
7. ĐẶT BEAM VÀO MODEL  →  8. XÁC NHẬN KẾT QUẢ
```

---

## BƯỚC 1 — KIỂM TRA KẾT NỐI VÀ THU THẬP YÊU CẦU

Trước khi chạy, xác nhận với user:
- **Tầng nào?** (ví dụ: LEVEL 3, LEVEL 5...)
- **Family gốc?** (mặc định: `M_Concrete-Rectangular Beam`)
- **Z-offset mặc định?** (thường: -50mm cho tất cả beam)
- **Beam đặc biệt?** (ví dụ: 250x600 offset -100mm)
- **Mapping width → type?** (xem Bước 5)

Kiểm tra kết nối Revit:
```python
print(doc.Title)
```

---

## BƯỚC 2 — TÌM CAD FILE THEO TẦNG

### 2a. List tất cả CAD Link Types
```python
cad_types = DB.FilteredElementCollector(doc).OfClass(DB.CADLinkType).ToElements()
for ct in cad_types:
    name = ct.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
    print(name)
```

### 2b. Tìm CAD cho tầng cụ thể
Tìm theo pattern tên file: `FP0X` (framing plan) hoặc `Level X`:
```python
target_name = "S_HH2C_FP03_001"  # pattern cho tầng 3
target_type = None
for ct in cad_types:
    name = ct.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
    if target_name in name:
        target_type = ct
        break
```

### 2c. Lấy ImportInstance từ CAD Type
```python
import_instances = DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance).ToElements()
target_instance = None
for imp in import_instances:
    if imp.GetTypeId() == target_type.Id:
        target_instance = imp
        break
```

> ⚠️ Nếu có nhiều instance cùng type (CAD import nhiều lần), chọn instance có level phù hợp hoặc hỏi user.

---

## BƯỚC 3 — TÌM VÀ ĐỌC LAYER BEAM

### 3a. List tất cả sub-categories (layers)
```python
import_cat = target_instance.Category
for sc in import_cat.SubCategories:
    name = getattr(sc, 'Name', '')
    if 'beam' in name.lower() or 'BEAM' in name:
        print("BEAM LAYER: " + name)
```

### 3b. Lấy GraphicsStyle ID của layer beam
```python
beam_sub_cat = None
for sc in import_cat.SubCategories:
    if 'SUB-BEAM' in getattr(sc, 'Name', '').upper():
        beam_sub_cat = sc
        break

beam_gs_id = beam_sub_cat.GetGraphicsStyle(DB.GraphicsStyleType.Projection).Id
```

> ⚠️ **Quan trọng:** Dùng `GetGraphicsStyle().Id` — KHÔNG dùng `beam_sub_cat.Id` trực tiếp. Hai ID này khác nhau.

### 3c. Quét geometry lấy đường thuộc layer beam
```python
opt = DB.Options()
geo_elem = target_instance.get_Geometry(opt)
raw_curves = []

def scan_geo(geo_iterable, transform=None):
    for obj in geo_iterable:
        if isinstance(obj, DB.GeometryInstance):
            scan_geo(obj.GetInstanceGeometry(), obj.Transform)
        elif isinstance(obj, (DB.Line, DB.Curve)):
            try:
                if obj.GraphicsStyleId == beam_gs_id:
                    if transform:
                        raw_curves.append(obj.CreateTransformed(transform))
                    else:
                        raw_curves.append(obj)
            except:
                pass

scan_geo(geo_elem)
print("Curves found: {}".format(len(raw_curves)))
```

---

## BƯỚC 4 — GHÉP CẶP ĐƯỜNG SONG SONG → CENTERLINE

CAD vẽ beam bằng 2 đường song song (+ 2 đầu hồi). Cần ghép cặp để tìm centerline.

### 4a. Phân loại đường ngang / dọc
```python
import math
FT_TO_MM = 304.8

lines_h, lines_v = [], []
for c in raw_curves:
    sp = c.GetEndPoint(0)
    ep = c.GetEndPoint(1)
    dx, dy = ep.X - sp.X, ep.Y - sp.Y
    length_2d = math.sqrt(dx*dx + dy*dy) * FT_TO_MM
    if length_2d < 10:
        continue
    angle = abs(math.degrees(math.atan2(dy, dx))) % 180
    entry = {
        'x1': sp.X*FT_TO_MM, 'y1': sp.Y*FT_TO_MM,
        'x2': ep.X*FT_TO_MM, 'y2': ep.Y*FT_TO_MM,
        'z': sp.Z*FT_TO_MM, 'length': length_2d
    }
    if angle < 10 or angle > 170:
        lines_h.append(entry)
    elif 80 < angle < 100:
        lines_v.append(entry)
```

### 4b. Ghép cặp đường ngang (Horizontal)
```python
def pair_lines_h(lines):
    pairs = []
    used = set()
    for i, l1 in enumerate(lines):
        if i in used: continue
        best_j, best_dist = None, None
        for j, l2 in enumerate(lines):
            if j <= i or j in used: continue
            min1, max1 = min(l1['x1'],l1['x2']), max(l1['x1'],l1['x2'])
            min2, max2 = min(l2['x1'],l2['x2']), max(l2['x1'],l2['x2'])
            overlap = min(max1,max2) - max(min1,min2)
            min_len = min(max1-min1, max2-min2)
            if min_len < 1 or overlap/min_len < 0.7: continue
            dist = abs(l1['y1'] - l2['y1'])
            if dist < 50 or dist > 1500: continue   # beam width range: 50–1500mm
            if best_dist is None or dist < best_dist:
                best_dist = dist; best_j = j
        if best_j is not None:
            l2 = lines[best_j]
            x_start = (min(l1['x1'],l1['x2']) + min(l2['x1'],l2['x2'])) / 2
            x_end   = (max(l1['x1'],l1['x2']) + max(l2['x1'],l2['x2'])) / 2
            cy = (l1['y1'] + l2['y1']) / 2
            pairs.append({
                'dir': 'H', 'main_s': x_start, 'main_e': x_end,
                'perp': cy, 'z': l1['z'],
                'width': round(abs(l1['y1'] - l2['y1']))
            })
            used.add(i); used.add(best_j)
    return pairs
```

### 4c. Ghép cặp đường dọc (Vertical)
```python
def pair_lines_v(lines):
    pairs = []
    used = set()
    for i, l1 in enumerate(lines):
        if i in used: continue
        best_j, best_dist = None, None
        for j, l2 in enumerate(lines):
            if j <= i or j in used: continue
            min1, max1 = min(l1['y1'],l1['y2']), max(l1['y1'],l1['y2'])
            min2, max2 = min(l2['y1'],l2['y2']), max(l2['y1'],l2['y2'])
            overlap = min(max1,max2) - max(min1,min2)
            min_len = min(max1-min1, max2-min2)
            if min_len < 1 or overlap/min_len < 0.7: continue
            dist = abs(l1['x1'] - l2['x1'])
            if dist < 50 or dist > 1500: continue
            if best_dist is None or dist < best_dist:
                best_dist = dist; best_j = j
        if best_j is not None:
            l2 = lines[best_j]
            y_start = (min(l1['y1'],l1['y2']) + min(l2['y1'],l2['y2'])) / 2
            y_end   = (max(l1['y1'],l1['y2']) + max(l2['y1'],l2['y2'])) / 2
            cx = (l1['x1'] + l2['x1']) / 2
            pairs.append({
                'dir': 'V', 'main_s': y_start, 'main_e': y_end,
                'perp': cx, 'z': l1['z'],
                'width': round(abs(l1['x1'] - l2['x1']))
            })
            used.add(i); used.add(best_j)
    return pairs

h_pairs = pair_lines_h(lines_h)
v_pairs = pair_lines_v(lines_v)
all_pairs = h_pairs + v_pairs
```

> 📐 **Nguyên lý ghép:** Hai đường song song có overlap ≥ 70% chiều dài và khoảng cách 50–1500mm → một beam. Width = khoảng cách giữa 2 đường.

---

## BƯỚC 5 — XÁC ĐỊNH TYPE MAPPING

### 5a. Kiểm tra widths có trong CAD
```python
widths = set(round(p['width']/50)*50 for p in all_pairs)
print("Widths found:", widths)
```

### 5b. Xác nhận mapping với user
Hỏi user mapping **width → beam type** và **z-offset**. Mặc định thường dùng:

| Width (mm) | Type mặc định | Z-offset |
|-----------|--------------|---------|
| 200 | 200 x 500mm | -50mm |
| 250 | 250 x 600mm | -50mm *(hoặc -100mm nếu đặc biệt)* |
| 300 | 300 x 600mm | -50mm |
| 400 | 400 x 800mm | -50mm |
| 500 | 500 x 1000mm | -50mm |

> ⚠️ Luôn xác nhận với user trước khi tạo — z-offset và type có thể thay đổi theo dự án.

---

## BƯỚC 6 — TẠO BEAM TYPE NẾU CHƯA CÓ

Xem file `references/create-beam-types.md` để biết cách tạo type trong family `M_Concrete-Rectangular Beam`.

Kiểm tra type đã tồn tại:
```python
symbols = DB.FilteredElementCollector(doc).OfClass(DB.FamilySymbol).ToElements()
beam_type_map = {
    s.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString(): s
    for s in symbols if s.Family.Name == 'M_Concrete-Rectangular Beam'
}
```

Tạo type mới nếu thiếu (xem references/create-beam-types.md).

---

## BƯỚC 7 — ĐẶT BEAM VÀO MODEL

```python
MM_TO_FT = 1.0 / 304.8
struct_type = DB.Structure.StructuralType.Beam

# Lấy level target
levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).ToElements()
target_level = next(lv for lv in levels if getattr(lv,'Name','') == 'LEVEL 3')

txn = DB.Transaction(doc, "Create Beams from CAD")
txn.Start()
try:
    created = 0
    for p in all_pairs:
        width_rounded = round(p['width'] / 50) * 50
        type_name = TYPE_MAP.get(width_rounded, DEFAULT_TYPE)
        fam_sym = beam_type_map.get(type_name)
        if not fam_sym: continue

        if not fam_sym.IsActive:
            fam_sym.Activate()
            doc.Regenerate()

        z_offset_mm = OFFSET_MAP.get(type_name, -50.0)
        z_ft = target_level.Elevation + (z_offset_mm * MM_TO_FT)

        if p['dir'] == 'H':
            sp = DB.XYZ(p['main_s']*MM_TO_FT, p['perp']*MM_TO_FT, z_ft)
            ep = DB.XYZ(p['main_e']*MM_TO_FT, p['perp']*MM_TO_FT, z_ft)
        else:
            sp = DB.XYZ(p['perp']*MM_TO_FT, p['main_s']*MM_TO_FT, z_ft)
            ep = DB.XYZ(p['perp']*MM_TO_FT, p['main_e']*MM_TO_FT, z_ft)

        if sp.DistanceTo(ep) < 0.1: continue  # bỏ qua beam quá ngắn (<30mm)

        line = DB.Line.CreateBound(sp, ep)
        beam = doc.Create.NewFamilyInstance(line, fam_sym, target_level, struct_type)
        created += 1

    txn.Commit()
    print("Created: {}".format(created))
except Exception as e:
    txn.RollbackIfNotCommitted()
    print("ERROR: " + str(e))
```

---

## BƯỚC 8 — XÁC NHẬN KẾT QUẢ

```python
beams_all = DB.FilteredElementCollector(doc)\
    .OfCategory(DB.BuiltInCategory.OST_StructuralFraming)\
    .OfClass(DB.FamilyInstance).ToElements()

# Lọc theo Z range của tầng vừa tạo
level_z_m = target_level.Elevation * 0.3048
new_beams = []
for b in beams_all:
    try:
        if 'Concrete-Rectangular Beam' not in b.Symbol.Family.Name: continue
        loc = b.Location
        if isinstance(loc, DB.LocationCurve):
            sp = loc.Curve.GetEndPoint(0)
            z_m = sp.Z * 0.3048
            if level_z_m - 0.2 < z_m <= level_z_m:
                new_beams.append(b)
    except:
        pass

from collections import Counter
type_check = Counter(
    b.Symbol.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
    for b in new_beams
)
print("=== VERIFICATION ===")
print("Total beams at level: {}".format(len(new_beams)))
for t, cnt in sorted(type_check.items()):
    print("  {}: {}".format(t, cnt))
```

---

## LƯU Ý QUAN TRỌNG

### Naming Convention — CAD Files (dự án HH2C)
| Tầng | Tên CAD file |
|------|-------------|
| Tầng 2 | `S_HH2C_FP02_001-2ND FLOOR FRAMING PLAN` |
| Tầng 3 | `S_HH2C_FP03_001-3RD FLOOR FRAMING PLAN` |
| Tầng 4 | `S_HH2C_FP04_001-4TH FLOOR FRAMING PLAN` |
| Tầng 5–7, 10–12... | `S_HH2C_FP05_001-TYPICAL 5-7TH...` |

### Layer Name Pattern
```
XR_HH2C_Level X-Floor Plan$0$S-_SUB-BEAM_H---
```

### Unit Conversion
- Revit internal = **feet**
- 1 mm = `1/304.8` feet
- Luôn convert khi set/get parameter: `mm * MM_TO_FT`

### Pitfalls thường gặp
| Vấn đề | Nguyên nhân | Giải pháp |
|--------|------------|-----------|
| 0 curves found | Dùng sai ID (subcategory vs GraphicsStyle) | Dùng `GetGraphicsStyle().Id` |
| Beam Z sai | Level elevation đo từ project base | `level.Elevation + offset_ft` |
| FamilySymbol not active | Chưa kích hoạt trước khi dùng | `fam_sym.Activate(); doc.Regenerate()` |
| Beam quá ngắn (error) | Đường CAD đầu hồi bị ghép nhầm | Check `sp.DistanceTo(ep) < 0.1` |
| Type không tìm thấy | Tên type không khớp | Kiểm tra `beam_type_map.keys()` |

---

## THAM KHẢO CHI TIẾT

- `references/create-beam-types.md` — Tạo mới family type trong M_Concrete-Rectangular Beam
- `references/cad-layer-patterns.md` — Danh sách layer patterns theo dự án
- `scripts/beam_from_cad.py` — Script hoàn chỉnh có thể copy vào execute_revit_code
