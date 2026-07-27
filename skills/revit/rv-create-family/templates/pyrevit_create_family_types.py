# pyRevit — Tạo family types từ plan JSON (build_type_catalog.py --json > plan.json).
# Batch-create family types in the OPEN family document from the plan JSON.
# Chạy TRONG Family Editor của Revit (pyRevit). Dùng Transaction. Không phải CLI của repo.
# -*- coding: utf-8 -*-
import json
from Autodesk.Revit.DB import Transaction

doc = __revit__.ActiveUIDocument.Document  # noqa: F821 (pyRevit inject)

PLAN = r"C:\plan.json"     # JSON từ: python build_type_catalog.py types.csv --json > plan.json

# Chỉ chạy trong Family Editor (doc.IsFamilyDocument == True).
if not doc.IsFamilyDocument:
    raise Exception("Mo file .rfa trong Family Editor roi chay lai.")

with open(PLAN) as fh:
    plan = json.load(fh)

fm = doc.FamilyManager
existing = {t.Name for t in fm.Types}

# map tên tham số -> FamilyParameter (chỉ set tham số đã tồn tại trong family)
params_by_name = {p.Definition.Name: p for p in fm.Parameters}

made, skipped = 0, 0
t = Transaction(doc, "Create family types from plan")
t.Start()
for item in plan["types"]:
    name = item["name"]
    if name in existing:            # bỏ qua type đã có
        skipped += 1
        continue
    fm.NewType(name)                # NewType cũng đặt làm CurrentType
    for pname, raw in item["params"].items():
        fp = params_by_name.get(pname)
        if fp is None or raw in ("", None):
            continue                # tham số chưa có trong family / giá trị rỗng -> bỏ qua
        try:
            if fp.StorageType.ToString() == "Double":
                fm.Set(fp, float(raw))          # đơn vị nội bộ Revit — kiểm lại nếu cần đổi
            elif fp.StorageType.ToString() == "Integer":
                fm.Set(fp, int(float(raw)))
            else:
                fm.Set(fp, str(raw))            # String / ElementId(as text)
        except Exception:
            pass                                # giá trị không hợp — bỏ qua, xử lý thủ công
    made += 1
t.Commit()

print("Da tao {0} type moi, bo qua {1} type trung ten.".format(made, skipped))
