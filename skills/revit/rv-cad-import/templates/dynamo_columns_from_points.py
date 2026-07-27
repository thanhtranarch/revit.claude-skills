# Dynamo — Python node: tạo structural column tại điểm chèn block (build plan JSON).
# Create structural columns at CAD block insertion points from the build plan.
# IN[0] = đường dẫn plan.json (string); IN[1] = tên layer (string). OUT = list Id.
# Dynamo tự quản lý transaction qua TransactionManager.
import clr
clr.AddReference("RevitServices")
clr.AddReference("RevitAPI")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import (
    FilteredElementCollector, FamilySymbol, Level, XYZ, BuiltInCategory
)
from Autodesk.Revit.DB.Structure import StructuralType
import json

doc = DocumentManager.Instance.CurrentDBDocument

PLAN = IN[0]                    # noqa: F821 (Dynamo inject) — đường dẫn plan.json
LAYER = IN[1]                   # noqa: F821 — layer chứa block cột
MM_TO_FT = 1.0 / 304.8

with open(PLAN) as fh:
    data = json.load(fh)
points = []
for lay in data["layers"]:
    if lay["layer"] == LAYER:
        points = lay.get("points", [])

symbol = (FilteredElementCollector(doc)
          .OfClass(FamilySymbol)
          .OfCategory(BuiltInCategory.OST_StructuralColumns)
          .FirstElement())
level = FilteredElementCollector(doc).OfClass(Level).FirstElement()

made = []
TransactionManager.Instance.EnsureInTransaction(doc)
if symbol and not symbol.IsActive:
    symbol.Activate()
for x, y in points:
    location = XYZ(x * MM_TO_FT, y * MM_TO_FT, 0.0)
    inst = doc.Create.NewFamilyInstance(location, symbol, level, StructuralType.Column)
    made.append(inst.Id.IntegerValue)
TransactionManager.Instance.TransactionTaskDone()

OUT = made  # noqa: F821 (Dynamo inject)
