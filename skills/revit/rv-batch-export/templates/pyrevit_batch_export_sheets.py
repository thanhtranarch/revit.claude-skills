# pyRevit — Export hàng loạt sheet ra PDF theo tên chuẩn.
# Chạy trong Revit 2022+ (dùng PDFExportOptions). Không phải CLI của repo.
# Chỉ đọc model + ghi PDF ra OUTPUT_DIR → không cần Transaction.
# -*- coding: utf-8 -*-
import os
import re
from Autodesk.Revit.DB import (
    FilteredElementCollector, ViewSheet, PDFExportOptions, ElementId
)

doc = __revit__.ActiveUIDocument.Document  # noqa: F821 (pyRevit inject)

OUTPUT_DIR = r"C:\Exports"                       # đổi thư mục đích
NAME_TEMPLATE = "{number}-{name}-{rev}"          # quy ước tên file
INVALID = re.compile(r'[\\/:*?"<>|]')            # ký tự không hợp lệ trên Windows


def clean(text):
    return INVALID.sub("_", (text or "").strip())


def sheet_filename(sheet):
    # Lấy revision hiện hành qua tham số hiển thị "Current Revision".
    rev_param = sheet.LookupParameter("Current Revision")
    rev_val = rev_param.AsString() if rev_param else ""
    return NAME_TEMPLATE.format(
        number=clean(sheet.SheetNumber),
        name=clean(sheet.Name),
        rev=clean(rev_val) or "A",
    )


# Thu thập sheet có thể in (bỏ placeholder).
sheets = [s for s in FilteredElementCollector(doc).OfClass(ViewSheet)
          if not s.IsPlaceholder]

if not os.path.isdir(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

exported = 0
for sheet in sheets:
    opts = PDFExportOptions()
    opts.FileName = sheet_filename(sheet)     # tên file (không đuôi)
    opts.Combine = False                      # mỗi sheet 1 file PDF
    doc.Export(OUTPUT_DIR, [sheet.Id], opts)  # chỉ đọc + ghi file
    exported += 1

print("Đã export {0} sheet -> {1}".format(exported, OUTPUT_DIR))
