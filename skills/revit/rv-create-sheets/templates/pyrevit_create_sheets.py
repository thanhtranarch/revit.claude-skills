# pyRevit — Tạo sheet hàng loạt từ plan JSON (plan_sheets.py --json > sheets.json).
# Batch-create Revit sheets from the plan JSON.
# Chạy TRONG Revit (pyRevit). Dùng Transaction. Không phải CLI của repo.
# -*- coding: utf-8 -*-
import json
from Autodesk.Revit.DB import (
    FilteredElementCollector, FamilySymbol, BuiltInCategory, ViewSheet, Transaction
)

doc = __revit__.ActiveUIDocument.Document  # noqa: F821 (pyRevit inject)

PLAN = r"C:\sheets.json"          # JSON từ: python plan_sheets.py sheets.csv --json > sheets.json


def first_titleblock(document):
    return (FilteredElementCollector(document)
            .OfClass(FamilySymbol)
            .OfCategory(BuiltInCategory.OST_TitleBlocks)
            .FirstElement())


with open(PLAN) as fh:
    plan = json.load(fh)

titleblock = first_titleblock(doc)          # đổi để chọn đúng titleblock theo tên
existing = {s.SheetNumber for s in FilteredElementCollector(doc).OfClass(ViewSheet)}

made = 0
t = Transaction(doc, "Create sheets from list")
t.Start()
for item in plan["sheets"]:
    if item["number"] in existing:          # bỏ qua sheet đã tồn tại
        continue
    sheet = ViewSheet.Create(doc, titleblock.Id)
    sheet.SheetNumber = item["number"]
    sheet.Name = item["name"]
    made += 1
t.Commit()

print("Da tao {0} sheet moi (bo qua sheet trung so).".format(made))
