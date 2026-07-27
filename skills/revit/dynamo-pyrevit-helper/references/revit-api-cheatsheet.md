# Revit API cheatsheet — pattern & bẫy thường gặp

## Thu thập phần tử / collect elements
```python
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory
walls = (FilteredElementCollector(doc)
         .OfCategory(BuiltInCategory.OST_Walls)
         .WhereElementIsNotElementType()   # bỏ element type, lấy instance
         .ToElements())
```
- `.WhereElementIsElementType()` để lấy **type**; `.WhereElementIsNotElementType()`
  để lấy **instance**. Nhầm hai cái này là lỗi phổ biến nhất.

## Transaction (chỉ pyRevit; Dynamo tự lo)
```python
t = Transaction(doc, "Tên thao tác")
t.Start()
try:
    ...   # mọi thay đổi model ở đây
    t.Commit()
except Exception:
    t.RollBack(); raise
```
- Trong **Dynamo Python node**: KHÔNG tạo Transaction thủ công — Dynamo mở sẵn.
  Nếu cần transaction con, dùng `TransactionManager.Instance`.

## Tham số / parameters
```python
p = el.LookupParameter("Comments")     # theo tên hiển thị
if p and not p.IsReadOnly:
    p.Set(value)                       # kiểu phải khớp StorageType
```
- Kiểm tra `p is not None` và `p.IsReadOnly` trước khi `.Set()`.
- `StorageType`: `String / Integer / Double / ElementId`. Set sai kiểu → lỗi.
- Param theo GUID (shared): `el.get_Parameter(guid)`.

## Đơn vị / units (Revit lưu nội bộ theo feet)
```python
from Autodesk.Revit.DB import UnitUtils, UnitTypeId
mm = UnitUtils.ConvertFromInternalUnits(value_ft, UnitTypeId.Millimeters)
ft = UnitUtils.ConvertToInternalUnits(value_mm, UnitTypeId.Millimeters)
```
- Đừng hard-code hệ số 304.8 — dùng `UnitUtils`. (Revit ≤2021 dùng `DisplayUnitType`.)

## Bẫy thường gặp / common pitfalls
- IronPython 2.7 (pyRevit CPython option / Dynamo cũ) vs CPython3 — cú pháp
  `print`, `unicode`, chia số nguyên khác nhau. Ghi rõ runtime.
- `el.Name` có thể ném lỗi với vài loại element → bọc `try/except`.
- Sửa model ngoài Transaction → `Autodesk.Revit.Exceptions.InvalidOperationException`.
- Không commit/rollback → transaction treo, Revit báo lỗi khi đóng.
```
