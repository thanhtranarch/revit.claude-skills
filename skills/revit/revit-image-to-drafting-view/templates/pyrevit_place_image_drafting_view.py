# pyRevit — Tạo Drafting View và đặt ảnh raster để trace (Revit 2022+).
# Create a drafting view and place a raster image for tracing.
# Chạy TRONG Revit (pyRevit). Dùng Transaction. Không phải CLI của repo.
# API ImageType/ImageInstance khác nhau theo phiên bản Revit — kiểm trước khi
# chạy hàng loạt. Lấy WIDTH_FT từ: python image_scale.py <img> --real-width-mm ...
# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import (
    FilteredElementCollector, ViewFamilyType, ViewFamily, ViewDrafting,
    ImageType, ImageTypeOptions, ImageTypeSource, ImageInstance,
    ImagePlacementOptions, BoxPlacement, XYZ, Transaction, BuiltInParameter
)

doc = __revit__.ActiveUIDocument.Document  # noqa: F821 (pyRevit inject)

IMAGE_PATH = r"C:\sketch.png"       # ảnh cần đặt
VIEW_NAME = "TRACE - Sketch"        # tên drafting view sẽ tạo
WIDTH_FT = 10000.0 / 304.8          # bề rộng đặt (mm→ft) — lấy từ image_scale.py


def drafting_view_type(document):
    for vft in FilteredElementCollector(document).OfClass(ViewFamilyType):
        if vft.ViewFamily == ViewFamily.Drafting:
            return vft
    return None


t = Transaction(doc, "Image to drafting view")
t.Start()

view = ViewDrafting.Create(doc, drafting_view_type(doc).Id)
try:
    view.Name = VIEW_NAME
except Exception:                    # tên trùng → giữ tên mặc định
    pass

image_type = ImageType.Create(
    doc, ImageTypeOptions(IMAGE_PATH, False, ImageTypeSource.Import))
placement = ImagePlacementOptions(XYZ.Zero, BoxPlacement.Center)
instance = ImageInstance.Create(doc, view, image_type.Id, placement)

width_param = instance.get_Parameter(BuiltInParameter.RASTER_SYMBOL_WIDTH)
if width_param and not width_param.IsReadOnly:
    width_param.Set(WIDTH_FT)        # đặt bề rộng theo cỡ thật; cao tự theo tỷ lệ

t.Commit()

print("Da tao drafting view '{0}' va dat anh (Width {1:.2f} ft)".format(
    view.Name, WIDTH_FT))
