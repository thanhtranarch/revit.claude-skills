# Dynamo — Python node: thu thập phần tử theo category.
# KHÔNG tự mở Transaction trong Dynamo (Dynamo tự quản lý).
# IN[0] = Category (Revit.Elements.Category); OUT = danh sách element.
import clr
clr.AddReference("RevitServices")
clr.AddReference("RevitAPI")
from RevitServices.Persistence import DocumentManager
from Autodesk.Revit.DB import FilteredElementCollector, ElementId

doc = DocumentManager.Instance.CurrentDBDocument

# IN[0] là Category từ node Dynamo; lấy BuiltInCategory id.
category = IN[0]                      # noqa: F821 (Dynamo inject)
bic_id = ElementId(category.Id)

elements = (FilteredElementCollector(doc)
            .OfCategoryId(bic_id)
            .WhereElementIsNotElementType()
            .ToElements())

# Trả tên + id để kiểm tra nhanh trong Dynamo.
OUT = [(e.Name, e.Id.IntegerValue) for e in elements]  # noqa: F821
