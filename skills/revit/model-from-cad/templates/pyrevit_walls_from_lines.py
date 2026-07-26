# pyRevit — Tạo Wall từ line CAD theo build plan JSON (parse_dxf.py --json).
# Create Revit walls from CAD lines using the parse_dxf build plan.
# Chạy TRONG Revit (pyRevit). Dùng Transaction để tạo phần tử. Không phải CLI repo.
# -*- coding: utf-8 -*-
import json
from Autodesk.Revit.DB import (
    FilteredElementCollector, WallType, Level, Line, XYZ, Wall, Transaction
)

doc = __revit__.ActiveUIDocument.Document  # noqa: F821 (pyRevit inject)

PLAN = r"C:\plan.json"        # JSON xuất từ: python parse_dxf.py plan.dxf --json > plan.json
LAYER = "WALL"                # layer chứa line tường
WALL_HEIGHT_FT = 10.0         # cao tường (feet)
MM_TO_FT = 1.0 / 304.8        # DXF thường theo mm; đổi sang feet (đơn vị nội bộ Revit)


def load_segments(plan_path, layer):
    with open(plan_path) as fh:
        data = json.load(fh)
    for lay in data["layers"]:
        if lay["layer"] == layer:
            return lay.get("segments", [])
    return []


segments = load_segments(PLAN, LAYER)
level = FilteredElementCollector(doc).OfClass(Level).FirstElement()
wall_type = FilteredElementCollector(doc).OfClass(WallType).FirstElement()

made = 0
t = Transaction(doc, "Walls from CAD")
t.Start()
for (x1, y1), (x2, y2) in segments:
    p1 = XYZ(x1 * MM_TO_FT, y1 * MM_TO_FT, 0.0)
    p2 = XYZ(x2 * MM_TO_FT, y2 * MM_TO_FT, 0.0)
    if p1.DistanceTo(p2) < 1e-6:
        continue
    curve = Line.CreateBound(p1, p2)
    Wall.Create(doc, curve, wall_type.Id, level.Id, WALL_HEIGHT_FT, 0.0, False, False)
    made += 1
t.Commit()

print("Da tao {0} wall tu layer {1}".format(made, LAYER))
