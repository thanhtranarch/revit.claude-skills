# IronPython Patterns — Revit MCP Connector

Các pattern hay gặp lỗi khi viết IronPython qua revit-mcp.

## Imports cần thiết
```python
import math
import clr
clr.AddReference('System')
from System.Collections.Generic import List as SList
```

## ElementId collection cho doc.Delete()
```python
# ĐÚNG
id_list = SList[DB.ElementId](list_of_element_ids)
doc.Delete(id_list)

# SAI — List[ElementId] không import được trực tiếp
List[DB.ElementId](...)  # NameError
```

## Lấy tên element an toàn
```python
# ĐÚNG
name = getattr(elem, 'Name', None)
if not name:
    p = elem.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
    name = p.AsString() if p else str(elem.Id.IntegerValue)

# SAI — thường gây AttributeError với FamilySymbol
elem.Name  # AttributeError: Name
```

## Transaction pattern
```python
t = DB.Transaction(doc, "Tên transaction")
t.Start()
# ... code thay đổi model ...
t.Commit()

# Không dùng t.RollbackOnError() — method này không tồn tại trong IronPython binding
# Thay bằng:
try:
    t.Start()
    # ... 
    t.Commit()
except Exception as ex:
    if t.GetStatus() == DB.TransactionStatus.Started:
        t.RollBack()
    print("Error: {}".format(ex))
```

## Group operations
```python
# Ungroup
grp_elem.UngroupMembers()  # trả về ICollection<ElementId>

# Regroup — LUÔN phải set tên lại
id_list = SList[DB.ElementId](member_ids)
new_group = doc.Create.NewGroup(id_list)
new_gt = doc.GetElement(new_group.GetTypeId())
new_gn = new_gt.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
if new_gn and not new_gn.IsReadOnly:
    new_gn.Set("TÊN_GROUP_CỤ")  # BẮT BUỘC — Revit tự đặt "Group 1", "Group 2"...
```

## Structural column placement
```python
structural_type = DB.Structure.StructuralType.Column
col = doc.Create.NewFamilyInstance(
    insertion_point,   # DB.XYZ (feet)
    family_symbol,     # FamilySymbol đã Activate()
    level,             # Level element
    structural_type
)

# Activate symbol nếu chưa active
if not col_sym.IsActive:
    col_sym.Activate()
    doc.Regenerate()

# Set chiều cao (top offset)
top_p = col.get_Parameter(DB.BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM)
if top_p and not top_p.IsReadOnly:
    top_p.Set(height_in_feet)

# Rotate
if abs(angle) > 0.001 and abs(abs(angle) - math.pi) > 0.001:
    axis = DB.Line.CreateBound(pt, DB.XYZ(pt.X, pt.Y, pt.Z + 1.0))
    DB.ElementTransformUtils.RotateElement(doc, col.Id, axis, angle)
```

## Dimension creation
```python
# 1. Dim type phải là object, không phải ElementId
dim_type = doc.GetElement(DB.ElementId(TYPE_ID))  # trả về DimensionType

# 2. Grid reference: dùng DB.Reference(elem), không phải Curve.Reference
grid_ref = DB.Reference(grid_element)

# 3. Column face reference: lấy từ GetSymbolGeometry()
opt = DB.Options()
opt.ComputeReferences = True
opt.View = view
for obj in col.get_Geometry(opt):
    if hasattr(obj, 'GetInstanceGeometry'):
        for sym_obj in obj.GetSymbolGeometry():
            if hasattr(sym_obj, 'Faces'):
                for face in sym_obj.Faces:
                    ref = face.Reference  # có thể None
                    normal = face.FaceNormal

# 4. ReferenceArray
ref_arr = DB.ReferenceArray()
ref_arr.Append(ref1)
ref_arr.Append(ref2)

# 5. Line đủ dài để cross cả 2 reference points
line = DB.Line.CreateBound(
    DB.XYZ(x_min - 1.0, y, z),
    DB.XYZ(x_max + 1.0, y, z)
)
dim = doc.Create.NewDimension(view, line, ref_arr, dim_type)
```

## Unit conversion
```python
# mm → feet
value_ft = value_mm / 304.8

# feet → mm  
value_mm = value_ft * 304.8

# Snap về 0 hoặc 5mm
def snap_to_5(v_mm):
    return round(v_mm / 5.0) * 5.0

# Check clean (tolerance 0.01mm = floating point safe)
def is_clean(v_mm):
    return abs(v_mm - snap_to_5(v_mm)) < 0.01
```

## Bounding box (XY overlap check)
```python
bb = elem.get_BoundingBox(None)  # None = model space, không filter theo view
if bb:
    minX = bb.Min.X * 304.8
    minY = bb.Min.Y * 304.8
    maxX = bb.Max.X * 304.8
    maxY = bb.Max.Y * 304.8

def bb_overlap(a, b, tol=1.0):
    return (a['minX'] < b['maxX'] - tol and a['maxX'] > b['minX'] + tol and
            a['minY'] < b['maxY'] - tol and a['maxY'] > b['minY'] + tol)
```

## Common BuiltInParameter references
```python
DB.BuiltInParameter.SYMBOL_NAME_PARAM         # Type name
DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM    # Wall unconnected height
DB.BuiltInParameter.WALL_BASE_OFFSET          # Wall base offset
DB.BuiltInParameter.WALL_ATTR_WIDTH_PARAM     # Wall type thickness
DB.BuiltInParameter.FAMILY_LEVEL_PARAM        # Column/family base level
DB.BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM  # Column top offset
DB.BuiltInParameter.DATUM_TEXT                # Grid name
DB.BuiltInParameter.ALL_MODEL_TYPE_NAME       # Alternative type name
```
