---
name: rvstr-column-tools
description: >
  Bộ công cụ Revit IronPython tự động hoá 3 tác vụ structural column: (1) REPLACE WALLS → COLUMNS: phát hiện wall override đỏ trong view, ungroup, xoá wall, đặt DPA_SC_COLUMN_RECTANGULAR đúng kích thước/vị trí/rotation, regroup lại. (2) EXTRACT COORDINATES: trích xuất X/Y/Z (mm, 10 chữ số) của column/wall kèm ID/Type/Level/Group, hiển thị bảng interactive, snap tọa độ về 0 hoặc 5mm, kiểm tra khoảng cách đến grid theo ΔX và ΔY riêng biệt. (3) DIM TO GRID: tạo 2 dimension lines/cột (X và Y) từ column face đến grid gần nhất, dùng type DPA-DIM-2.5mm Check. LUÔN dùng skill này khi user nhắc: "thay tường bằng cột", "replace wall by column", "trích xuất tọa độ cột/tường", "extract coordinates", "dim cột đến grid", "dimension to grid", "snap tọa độ", "kiểm tra grid", hoặc bất kỳ kết hợp column + wall + grid + Revit.
license: MIT
compatibility: Requires Revit + pyRevit/IronPython MCP connector; edits columns, walls and dimensions inside a Transaction. Reads before writing and confirms scope with the user.
metadata:
  software: revit
  discipline: structural
  category: automation
---

# Revit Column Tools

Skill thực thi IronPython qua MCP Revit connector. Gồm 3 module độc lập, có thể kết hợp theo thứ tự.

---

## MODULE 1 — Replace Walls by Structural Columns

### Mục đích
Tìm wall bị **graphic override màu đỏ** (Cut Lines + Cut Foreground = RGB 255,0,0) trong view hiện tại, thay thế bằng `DPA_SC_COLUMN_RECTANGULAR` với type khớp kích thước wall.

### Quy trình

**Bước 1 — Kiểm tra kết nối và thu thập dữ liệu**
```python
# Xác nhận Revit status trước khi thực hiện
# revit-connector:get_revit_status
```

**Bước 2 — Phát hiện wall đỏ**
```python
view = doc.ActiveView
collector = DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType()

red_walls = []
for wall in collector:
    ogs = view.GetElementOverrides(wall.Id)
    c = ogs.CutLineColor
    if c.IsValid and c.Red > 180 and c.Green < 80 and c.Blue < 80:
        red_walls.append(wall)
```

**Bước 3 — Thu thập thông tin wall (vị trí, kích thước, group, rotation)**
```python
import math
for wall in red_walls:
    loc = wall.Location
    curve = loc.Curve
    start, end = curve.GetEndPoint(0), curve.GetEndPoint(1)
    mid_x = (start.X + end.X) / 2.0
    mid_y = (start.Y + end.Y) / 2.0
    angle = math.atan2(end.Y - start.Y, end.X - start.X)
    w_mm = int(round(wall.Width * 304.8))
    l_mm = int(round(curve.Length * 304.8))
    h_ft = wall.get_Parameter(DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()
    col_type_name = "{}mm X {}mm".format(w_mm, l_mm)
    # thu thập group_id để regroup sau
```

**Bước 4 — Kiểm tra column family và types**
- Family: `DPA_SC_COLUMN_RECTANGULAR`
- Category: `OST_StructuralColumns`
- Lấy type name qua `SYMBOL_NAME_PARAM`
- Nếu type bị thiếu (ví dụ `3009mm` không tồn tại) → **remap về type gần nhất** (xem bảng TYPE_REMAP bên dưới)

**Bước 5 — Lấy base level của wall (QUAN TRỌNG)**
```python
# ĐÚNG: dùng FAMILY_BASE_LEVEL_PARAM để lấy level gốc của wall
# KHÔNG dùng FAMILY_LEVEL_PARAM (trả về level sai trên doc có nhiều tầng)
# Lấy level từ wall để truyền vào NewFamilyInstance() — KHÔNG dùng levels[0]
def get_wall_level(wall, doc):
    for param_id in [DB.BuiltInParameter.WALL_BASE_CONSTRAINT,
                     DB.BuiltInParameter.FAMILY_BASE_LEVEL_PARAM,
                     DB.BuiltInParameter.FAMILY_LEVEL_PARAM]:
        p = wall.get_Parameter(param_id)
        if p:
            lv = doc.GetElement(p.AsElementId())
            if lv and isinstance(lv, DB.Level):
                return lv
    return None
```

**Bước 6 — Transaction duy nhất: Snapshot → Ungroup → Xoá wall → Đặt cột → Regroup**
```python
from System.Collections.Generic import List as SList

t = DB.Transaction(doc, "Replace Walls by Columns")
t.Start()
try:
    # 6a. Snapshot tất cả element ID trong mỗi group TRƯỚC KHI ungroup
    # Bao gồm: walls sẽ bị xoá, doors, windows, generic models, annotations, v.v.
    grp_snapshot = {}   # {grp_id_int: set(ElementId)}
    grp_names   = {}   # {grp_id_int: grp_type_name}
    grp_ids_set = set()

    for d in wall_data:
        gid = d['grp_id']
        if gid and gid.IntegerValue != -1:
            grp_ids_set.add(gid.IntegerValue)

    for gid_int in grp_ids_set:
        grp_elem = doc.GetElement(DB.ElementId(gid_int))
        if not grp_elem:
            continue
        gt = doc.GetElement(grp_elem.GetTypeId())
        grp_names[gid_int] = gt.Name
        # GetMemberIds() trả về tất cả element thuộc group
        member_ids = grp_elem.GetMemberIds()
        grp_snapshot[gid_int] = set(mid.IntegerValue for mid in member_ids)

    # 6b. Ungroup tất cả
    for gid_int in grp_ids_set:
        grp_elem = doc.GetElement(DB.ElementId(gid_int))
        if grp_elem:
            grp_elem.UngroupMembers()

    # 6c. Xoá walls đỏ (chỉ wall có col_sym hợp lệ)
    wall_ids_to_del = SList[DB.ElementId](
        [d['id'] for d in wall_data if d['col_sym'] is not None]
    )
    deleted_wall_int_ids = set(eid.IntegerValue for eid in wall_ids_to_del)
    doc.Delete(wall_ids_to_del)

    # 6d. Đặt cột mới — map wall_id → col_id để biết cột thuộc group nào
    wall_to_col   = {}   # {wall_id_int: ElementId}   (để regroup)
    placed_results = []

    for d in wall_data:
        if d['col_sym'] is None:
            placed_results.append({
                'wall_id': d['id'].IntegerValue, 'col_id': '—',
                'type': '{}mm X {}mm'.format(d['w_mm'], d['l_mm']),
                'level': d['level_name'], 'group': d['grp_name'] or '—',
                'status': 'SKIPPED'
            })
            continue

        sym = d['col_sym']
        if not sym.IsActive:
            sym.Activate()
            doc.Regenerate()

        col_inst = doc.Create.NewFamilyInstance(
            d['mid'], sym, d['level'],
            DB.Structure.StructuralType.Column
        )
        top_p = col_inst.get_Parameter(DB.BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM)
        if top_p and not top_p.IsReadOnly:
            top_p.Set(d['h_ft'])

        ang = d['angle']
        if abs(ang) > 0.001 and abs(abs(ang) - math.pi) > 0.001:
            axis = DB.Line.CreateBound(d['mid'], DB.XYZ(d['mid'].X, d['mid'].Y, d['mid'].Z + 1))
            DB.ElementTransformUtils.RotateElement(doc, col_inst.Id, axis, ang)

        wall_to_col[d['id'].IntegerValue] = col_inst.Id
        placed_results.append({
            'wall_id': d['id'].IntegerValue, 'col_id': col_inst.Id.IntegerValue,
            'type': d['col_type_name'], 'level': d['level_name'],
            'group': d['grp_name'] or '—', 'status': 'OK'
        })

    # 6e. Regroup: snapshot (trừ walls đã xoá) + columns mới
    # Gom theo tên group (nhiều grp_id instance có thể share cùng type name)
    name_to_final_ids = {}   # {grp_name: [ElementId, ...]}

    for gid_int, member_int_ids in grp_snapshot.items():
        grp_name = grp_names[gid_int]
        final_ids = name_to_final_ids.setdefault(grp_name, [])

        for mid_int in member_int_ids:
            if mid_int in deleted_wall_int_ids:
                # Wall này đã xoá → thay bằng column mới tương ứng
                new_col_id = wall_to_col.get(mid_int)
                if new_col_id:
                    final_ids.append(new_col_id)
                # nếu SKIPPED thì bỏ qua (không thêm wall cũ lẫn cột mới)
            else:
                # Element khác (doors, windows, generic models, v.v.) → giữ lại
                final_ids.append(DB.ElementId(mid_int))

    for grp_name, elem_ids in name_to_final_ids.items():
        if not elem_ids:
            continue
        id_list = SList[DB.ElementId](elem_ids)
        new_grp = doc.Create.NewGroup(id_list)
        doc.Regenerate()
        grp_type = doc.GetElement(new_grp.GetTypeId())
        grp_type.Name = grp_name

    t.Commit()

except Exception as ex:
    t.Rollback()
    raise ex
```

**Bước 7 — Hiển thị bảng kết quả (BẮT BUỘC)**
```python
# placed_results đã được thu thập trong Bước 6c
# Dùng visualize:show_widget để render bảng HTML interactive
# Bảng phải có các cột: Wall ID | Column ID | Type | Level | Group | Status
# Color-code row: OK = xanh lá (#d1fae5), SKIPPED = vàng (#fef9c3)
# Hiển thị tổng: X replaced, Y skipped ở cuối bảng
```

### TYPE_REMAP (khi column type không tồn tại)
| Wall length (mm) | → Column type |
|---|---|
| 3009 | 500mm X 3000mm |
| 4355 | 500mm X 4350mm |
| Bất kỳ | Round về 5mm gần nhất |

### Lưu ý quan trọng
- `wall.GroupId.IntegerValue == -1` → wall không trong group
- Sau ungroup, `NewGroup()` tạo group mới với tên tự động → phải đặt lại tên qua `grp_type.Name = "..."` (không dùng SYMBOL_NAME_PARAM)
- `Location.Move()` không hoạt động khi element còn trong group
- Revit unit: **feet** nội bộ → nhân 304.8 để ra mm
- ❌ KHÔNG dùng `t.RollbackIfNotCommitted()` → dùng `t.Rollback()` thay thế
- ✅ **LUÔN** dùng `WALL_BASE_CONSTRAINT` để lấy level của wall, KHÔNG dùng `levels[0]` hay `FAMILY_LEVEL_PARAM` vì sẽ đặt cột sai tầng
- ✅ **BẮT BUỘC** hiển thị bảng kết quả sau khi replace xong, dùng `visualize:show_widget`

---

## MODULE 2 — Extract Coordinates (Column & Wall)

### Mục đích
Trích xuất tọa độ X, Y, Z (mm) của toàn bộ structural column hoặc wall trong view hiện tại. Hiển thị bảng interactive với filter, sort, search.

### Lấy tọa độ Column
```python
view = doc.ActiveView
col_collector = DB.FilteredElementCollector(doc, view.Id)\
    .OfCategory(DB.BuiltInCategory.OST_StructuralColumns)\
    .WhereElementIsNotElementType()

for col in col_collector:
    loc = col.Location
    if not loc or not hasattr(loc, 'Point'): continue
    pt = loc.Point
    x_mm = pt.X * 304.8
    y_mm = pt.Y * 304.8
    z_mm = pt.Z * 304.8

    # Type name
    type_elem = doc.GetElement(col.GetTypeId())
    tp = type_elem.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
    type_name = tp.AsString() if tp else "N/A"

    # Level
    lv_param = col.get_Parameter(DB.BuiltInParameter.FAMILY_LEVEL_PARAM)
    lv = doc.GetElement(lv_param.AsElementId()) if lv_param else None
    level_name = lv.Name if lv else "N/A"

    # Group
    grp_id = col.GroupId
    grp_name = "—"
    if grp_id and grp_id.IntegerValue != -1:
        grp_elem = doc.GetElement(grp_id)
        gt = doc.GetElement(grp_elem.GetTypeId())
        gn = gt.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
        grp_name = gn.AsString() if gn else "N/A"
```

### Lấy tọa độ Wall
```python
for wall in wall_collector:
    loc = wall.Location
    curve = loc.Curve
    start = curve.GetEndPoint(0)
    end = curve.GetEndPoint(1)
    mid_x = (start.X + end.X) / 2.0 * 304.8
    mid_y = (start.Y + end.Y) / 2.0 * 304.8
    length_mm = curve.Length * 304.8
    width_mm = wall.Width * 304.8
```

### Snap tọa độ về 0 hoặc 5
```python
def round_to_0_or_5(v):
    return round(v / 5.0) * 5.0

# Kiểm tra clean
def is_clean(v, tol=0.01):  # tolerance 0.01mm
    return abs(v - round_to_0_or_5(v)) < tol

# Move element (phải ungroup trước):
dx_ft = (round_to_0_or_5(px_mm) - px_mm) / 304.8
dy_ft = (round_to_0_or_5(py_mm) - py_mm) / 304.8
col.Location.Move(DB.XYZ(dx_ft, dy_ft, 0.0))
```

### Output format
Hiển thị bảng HTML interactive (dùng `visualize:show_widget`) với:
- Columns: ID | Type | Level | X (mm) | Y (mm) | Z (mm) | Group
- Filter/sort/search
- 10 chữ số thập phân khi user yêu cầu
- Color-coded theo trạng thái (nếu cần)

### Kiểm tra khoảng cách đến grid
```python
import math

def point_to_segment_dist_full(px, py, x0, y0, x1, y1):
    """Trả về (dist, delta_x, delta_y) — signed deltas theo 2 chiều"""
    dx, dy = x1 - x0, y1 - y0
    len2 = dx*dx + dy*dy
    if len2 == 0:
        return math.sqrt((px-x0)**2+(py-y0)**2), px-x0, py-y0
    t = max(0.0, min(1.0, ((px-x0)*dx+(py-y0)*dy)/len2))
    cx, cy = x0+t*dx, y0+t*dy
    ddx, ddy = px-cx, py-cy
    return math.sqrt(ddx*ddx+ddy*ddy), ddx, ddy

# Load grids (tất cả document, không filter theo view)
grid_collector = DB.FilteredElementCollector(doc)\
    .OfCategory(DB.BuiltInCategory.OST_Grids)\
    .WhereElementIsNotElementType()

for g in grid_collector:
    curve = g.Curve
    s, e = curve.GetEndPoint(0), curve.GetEndPoint(1)
    name_p = g.get_Parameter(DB.BuiltInParameter.DATUM_TEXT)
    gname = name_p.AsString() if name_p else str(g.Id.IntegerValue)
    # phân loại H/V grid theo dx vs dy
```

---

## MODULE 3 — Dimension Column to Nearest Grid

### Mục đích
Tạo **2 dimension lines** cho mỗi column trong view: một theo X (column face → vertical grid), một theo Y (column face → horizontal grid). Dùng dim type `DPA-DIM-2.5mm Check`.

### Phân loại grid
```python
# Horizontal grid (dx > dy) → đo khoảng cách Y
# Vertical grid   (dy > dx) → đo khoảng cách X
for g in grid_collector:
    s, e = curve.GetEndPoint(0), curve.GetEndPoint(1)
    dx, dy = abs(e.X - s.X), abs(e.Y - s.Y)
    if dx > dy:
        h_grids.append(...)  # measure Y
    else:
        v_grids.append(...)  # measure X
```

### Lấy face references từ column
```python
opt = DB.Options()
opt.ComputeReferences = True
opt.View = view
geo = col_elem.get_Geometry(opt)

for obj in geo:
    if hasattr(obj, 'GetInstanceGeometry'):
        sym_geo = obj.GetSymbolGeometry()
        for sym_obj in sym_geo:
            if hasattr(sym_obj, 'Faces'):
                for face in sym_obj.Faces:
                    ref = face.Reference
                    if ref:
                        face_refs.append({'ref': ref, 'normal': face.FaceNormal})

# Phân loại face theo normal
x_faces = [fr for fr in face_refs if abs(fr['normal'].X) > 0.9]
y_faces = [fr for fr in face_refs if abs(fr['normal'].Y) > 0.9]
```

### Lấy grid reference
```python
# ĐÚNG: dùng DB.Reference(grid_element) — không dùng Curve.Reference
gv_ref = DB.Reference(nearest_v_grid['elem'])
gh_ref = DB.Reference(nearest_h_grid['elem'])
```

### Tạo dimension
```python
dim_type = doc.GetElement(DB.ElementId(5408676))  # DPA-DIM-2.5mm Check

# X dim: horizontal line qua col Y, refs = v-grid + col x-face
ref_arr_x = DB.ReferenceArray()
ref_arr_x.Append(gv_ref)
ref_arr_x.Append(col_x_face_ref)

line_x = DB.Line.CreateBound(
    DB.XYZ(min(col_x, grid_x) - 1.0, col_y, col_z),
    DB.XYZ(max(col_x, grid_x) + 1.0, col_y, col_z)
)
doc.Create.NewDimension(view, line_x, ref_arr_x, dim_type)

# Y dim: vertical line qua col X, refs = h-grid + col y-face
ref_arr_y = DB.ReferenceArray()
ref_arr_y.Append(gh_ref)
ref_arr_y.Append(col_y_face_ref)

line_y = DB.Line.CreateBound(
    DB.XYZ(col_x, min(col_y, grid_y) - 1.0, col_z),
    DB.XYZ(col_x, max(col_y, grid_y) + 1.0, col_z)
)
doc.Create.NewDimension(view, line_y, ref_arr_y, dim_type)
```

### Dim type IDs (project CXL-DPA)
| Name | ID |
|---|---|
| DPA-DIM-2.5mm Check | 5408676 |
| DPA-DIM-2.5mm | 261 / 187755 |
| DPA-DIM-2.0mm | 248144 |
| DPA-DIM-1.5mm | 248296 |

> Nếu dim type ID không hợp lệ → fallback: lấy DimensionType đầu tiên có tên chứa "DPA-DIM"

---

## Lưu ý chung — IronPython + Revit API

| Vấn đề | Giải pháp |
|---|---|
| `List[ElementId]` | `from System.Collections.Generic import List as SList` |
| `t.RollbackIfNotCommitted()` không tồn tại | Dùng `t.Rollback()` trong except block |
| `element.Name` → AttributeError | Dùng `getattr(elem, 'Name', None)` hoặc `get_Parameter(SYMBOL_NAME_PARAM)` |
| Group bị rename sau `NewGroup()` | Dùng `grp_type.Name = "tên_group"` (property trực tiếp, không qua param) |
| `Location.Move()` fail khi trong group | Ungroup → move → regroup trong 1 transaction |
| Floating point residual sau convert ft↔mm | Tolerance 0.01mm cho "clean check", không dùng == |
| `doc.Create.NewDimension(view, line, refs, dim_type_id)` | Phải pass `DimensionType` object, không phải `ElementId` |
| Grid reference | Dùng `DB.Reference(grid_elem)`, không dùng `grid.Curve.Reference` |
| **Column đặt sai tầng** | **LUÔN dùng `WALL_BASE_CONSTRAINT` để lấy level từ wall gốc, truyền vào `NewFamilyInstance()`** |
| **Không thấy kết quả** | **BẮT BUỘC gọi `visualize:show_widget` hiển thị bảng Wall ID → Column ID sau replace** |

---

## Thứ tự thực hiện thường gặp

```
1. get_revit_status          → xác nhận kết nối
2. get_current_view_info     → lấy thông tin view đang mở
3. MODULE 1: Replace walls   → ungroup → xoá → đặt cột → regroup
4. MODULE 2: Snap toạ độ     → kiểm tra X/Y → snap về 0/5 nếu cần
5. MODULE 2: Extract + grid  → trích xuất tọa độ + khoảng cách đến grid
6. MODULE 3: Dim to grid     → tạo 2 dim/cột cho toàn view
```

Đọc thêm chi tiết tại:
- `references/ironpython-patterns.md` — các pattern IronPython thường gặp
- `references/project-ids.md` — Element IDs, Group IDs dự án CXL-DPA
