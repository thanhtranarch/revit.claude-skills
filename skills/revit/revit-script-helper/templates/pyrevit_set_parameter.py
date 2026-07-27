# pyRevit — Đặt tham số hàng loạt / Bulk-set a parameter (with Transaction).
# Chạy trong pyRevit (IronPython/CPython). Không phải CLI của repo.
# Sửa CATEGORY, PARAM_NAME, NEW_VALUE cho phù hợp.
# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import (
    FilteredElementCollector, BuiltInCategory, Transaction, StorageType
)

doc = __revit__.ActiveUIDocument.Document  # noqa: F821  (pyRevit inject)

CATEGORY = BuiltInCategory.OST_Walls
PARAM_NAME = "Comments"
NEW_VALUE = "Reviewed 2026"

elements = (FilteredElementCollector(doc)
            .OfCategory(CATEGORY)
            .WhereElementIsNotElementType()
            .ToElements())

updated, skipped = 0, 0
t = Transaction(doc, "Bulk set parameter")
t.Start()
try:
    for el in elements:
        p = el.LookupParameter(PARAM_NAME)
        # Bỏ qua nếu không có param, chỉ đọc, hoặc không phải kiểu chuỗi.
        if p is None or p.IsReadOnly or p.StorageType != StorageType.String:
            skipped += 1
            continue
        p.Set(NEW_VALUE)
        updated += 1
    t.Commit()
except Exception:
    t.RollBack()
    raise

print("Đã cập nhật {0}, bỏ qua {1}".format(updated, skipped))
