"""
beam_from_cad.py
================
Script hoàn chỉnh để tạo Structural Beam từ CAD layer trong Revit.
Chạy trong execute_revit_code (IronPython / pyRevit MCP).

CÁCH DÙNG:
1. Sửa phần CONFIG bên dưới
2. Copy toàn bộ script vào execute_revit_code
3. Chạy và xem kết quả

REQUIRES: revit-connector MCP, Revit doc đang mở
"""

import math
from collections import Counter

# ============================================================
# CONFIG — SỬA CÁC GIÁ TRỊ NÀY TRƯỚC KHI CHẠY
# ============================================================

# Tên tầng trong Revit
TARGET_LEVEL_NAME = "LEVEL 3"

# Pattern tên file CAD (một phần tên là đủ)
CAD_FILE_PATTERN = "FP03"

# Tên family gốc
FAMILY_NAME = "M_Concrete-Rectangular Beam"

# Mapping: width (mm, rounded to 50) -> type name
TYPE_MAP = {
    200: "200 x 500mm",
    250: "250 x 600mm",
    300: "300 x 600mm",
    400: "400 x 800mm",
    500: "500 x 1000mm",
}
DEFAULT_TYPE = "300 x 600mm"

# Z-offset mặc định (mm, âm = xuống)
DEFAULT_Z_OFFSET_MM = -50.0

# Override z-offset cho type đặc biệt: {type_name: offset_mm}
SPECIAL_OFFSET_MAP = {
    "250 x 600mm": -100.0,
}

# ============================================================
# CONSTANTS
# ============================================================
FT_TO_MM = 304.8
MM_TO_FT = 1.0 / FT_TO_MM

# ============================================================
# STEP 1: TÌM CAD INSTANCE
# ============================================================
print("=== STEP 1: Finding CAD file '{}' ===".format(CAD_FILE_PATTERN))

cad_types = DB.FilteredElementCollector(doc).OfClass(DB.CADLinkType).ToElements()
target_cad_type = None
for ct in cad_types:
    try:
        name = ct.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
        if CAD_FILE_PATTERN in name:
            target_cad_type = ct
            print("  Found: " + name)
            break
    except:
        pass

if not target_cad_type:
    print("ERROR: No CAD file matching '{}' found!".format(CAD_FILE_PATTERN))
    print("Available CAD files:")
    for ct in cad_types:
        try:
            print("  " + ct.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString())
        except:
            pass
    raise Exception("CAD file not found")

import_instances = DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance).ToElements()
target_instance = None
for imp in import_instances:
    if imp.GetTypeId() == target_cad_type.Id:
        target_instance = imp
        break

if not target_instance:
    raise Exception("ImportInstance not found for CAD type")

print("  Instance Id: {}".format(target_instance.Id.IntegerValue))

# ============================================================
# STEP 2: TÌM LAYER BEAM
# ============================================================
print("\n=== STEP 2: Finding beam layer ===")

import_cat = target_instance.Category
beam_sub_cat = None
for sc in import_cat.SubCategories:
    name = getattr(sc, 'Name', '')
    if 'SUB-BEAM' in name.upper():
        beam_sub_cat = sc
        print("  Found layer: " + name)
        break

if not beam_sub_cat:
    print("  'SUB-BEAM' not found. Available layers with 'beam':")
    for sc in import_cat.SubCategories:
        name = getattr(sc, 'Name', '')
        if 'beam' in name.lower():
            print("    " + name)
    raise Exception("Beam layer not found")

beam_gs_id = beam_sub_cat.GetGraphicsStyle(DB.GraphicsStyleType.Projection).Id
print("  GraphicsStyle Id: {}".format(beam_gs_id.IntegerValue))

# ============================================================
# STEP 3: QUÉT GEOMETRY
# ============================================================
print("\n=== STEP 3: Scanning geometry ===")

opt = DB.Options()
geo_elem = target_instance.get_Geometry(opt)
raw_curves = []

def scan_geo(geo_iterable, transform=None):
    for obj in geo_iterable:
        if isinstance(obj, DB.GeometryInstance):
            scan_geo(obj.GetInstanceGeometry(), obj.Transform)
        elif isinstance(obj, (DB.Line, DB.Curve)):
            try:
                if obj.GraphicsStyleId == beam_gs_id:
                    if transform:
                        raw_curves.append(obj.CreateTransformed(transform))
                    else:
                        raw_curves.append(obj)
            except:
                pass

scan_geo(geo_elem)
print("  Raw curves: {}".format(len(raw_curves)))

# ============================================================
# STEP 4: PHÂN LOẠI & GHÉP CẶP
# ============================================================
print("\n=== STEP 4: Pairing parallel lines ===")

lines_h, lines_v = [], []
for c in raw_curves:
    try:
        sp = c.GetEndPoint(0)
        ep = c.GetEndPoint(1)
        dx = ep.X - sp.X
        dy = ep.Y - sp.Y
        length_2d = math.sqrt(dx*dx + dy*dy) * FT_TO_MM
        if length_2d < 10:
            continue
        angle = abs(math.degrees(math.atan2(dy, dx))) % 180
        entry = {
            'x1': sp.X*FT_TO_MM, 'y1': sp.Y*FT_TO_MM,
            'x2': ep.X*FT_TO_MM, 'y2': ep.Y*FT_TO_MM,
            'z': sp.Z*FT_TO_MM, 'length': length_2d
        }
        if angle < 10 or angle > 170:
            lines_h.append(entry)
        elif 80 < angle < 100:
            lines_v.append(entry)
    except:
        pass

def pair_lines(lines, main_keys, perp_key):
    pairs = []
    used = set()
    k1, k2 = main_keys
    for i, l1 in enumerate(lines):
        if i in used: continue
        best_j, best_dist = None, None
        for j, l2 in enumerate(lines):
            if j <= i or j in used: continue
            min1, max1 = min(l1[k1], l1[k2]), max(l1[k1], l1[k2])
            min2, max2 = min(l2[k1], l2[k2]), max(l2[k1], l2[k2])
            overlap = min(max1, max2) - max(min1, min2)
            min_len = min(max1-min1, max2-min2)
            if min_len < 1 or overlap/min_len < 0.7: continue
            dist = abs(l1[perp_key] - l2[perp_key])
            if dist < 50 or dist > 1500: continue
            if best_dist is None or dist < best_dist:
                best_dist = dist; best_j = j
        if best_j is not None:
            l2 = lines[best_j]
            s = (min(l1[k1],l1[k2]) + min(l2[k1],l2[k2])) / 2
            e = (max(l1[k1],l1[k2]) + max(l2[k1],l2[k2])) / 2
            cp = (l1[perp_key] + l2[perp_key]) / 2
            pairs.append({'main_s': s, 'main_e': e, 'perp': cp,
                         'z': l1['z'], 'width': round(abs(l1[perp_key]-l2[perp_key]))})
            used.add(i); used.add(best_j)
    return pairs

h_raw = pair_lines(lines_h, ('x1','x2'), 'y1')
v_raw = pair_lines(lines_v, ('y1','y2'), 'x1')

# Add direction
h_pairs = [dict(p, dir='H') for p in h_raw]
v_pairs = [dict(p, dir='V') for p in v_raw]
all_pairs = h_pairs + v_pairs

widths = Counter(round(p['width']/50)*50 for p in all_pairs)
print("  Pairs found: {} (H={}, V={})".format(len(all_pairs), len(h_pairs), len(v_pairs)))
print("  Widths: " + str(dict(widths)))

# ============================================================
# STEP 5: PREPARE FAMILY SYMBOLS & LEVEL
# ============================================================
print("\n=== STEP 5: Preparing symbols and level ===")

symbols = DB.FilteredElementCollector(doc).OfClass(DB.FamilySymbol).ToElements()
beam_type_map = {}
for s in symbols:
    if s.Family.Name == FAMILY_NAME:
        name = s.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        beam_type_map[name] = s

print("  Available types: {}".format(sorted(beam_type_map.keys())))

levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).ToElements()
target_level = None
for lv in levels:
    if getattr(lv, 'Name', '') == TARGET_LEVEL_NAME:
        target_level = lv
        break

if not target_level:
    raise Exception("Level '{}' not found!".format(TARGET_LEVEL_NAME))

print("  Level: {} | El={:.3f}m".format(TARGET_LEVEL_NAME, target_level.Elevation*0.3048))

struct_type = DB.Structure.StructuralType.Beam

# ============================================================
# STEP 6: CREATE BEAMS
# ============================================================
print("\n=== STEP 6: Creating beams ===")

created = 0
skipped = 0
errors = []

txn = DB.Transaction(doc, "Create Beams from CAD - {}".format(TARGET_LEVEL_NAME))
txn.Start()
try:
    for p in all_pairs:
        width_rounded = round(p['width'] / 50) * 50
        type_name = TYPE_MAP.get(width_rounded, DEFAULT_TYPE)
        fam_sym = beam_type_map.get(type_name)

        if not fam_sym:
            errors.append("Type not found: {}".format(type_name))
            skipped += 1
            continue

        if not fam_sym.IsActive:
            fam_sym.Activate()
            doc.Regenerate()

        z_offset_mm = SPECIAL_OFFSET_MAP.get(type_name, DEFAULT_Z_OFFSET_MM)
        z_ft = target_level.Elevation + (z_offset_mm * MM_TO_FT)

        if p['dir'] == 'H':
            sp = DB.XYZ(p['main_s']*MM_TO_FT, p['perp']*MM_TO_FT, z_ft)
            ep = DB.XYZ(p['main_e']*MM_TO_FT, p['perp']*MM_TO_FT, z_ft)
        else:
            sp = DB.XYZ(p['perp']*MM_TO_FT, p['main_s']*MM_TO_FT, z_ft)
            ep = DB.XYZ(p['perp']*MM_TO_FT, p['main_e']*MM_TO_FT, z_ft)

        if sp.DistanceTo(ep) < 0.1:
            skipped += 1
            continue

        try:
            line = DB.Line.CreateBound(sp, ep)
            doc.Create.NewFamilyInstance(line, fam_sym, target_level, struct_type)
            created += 1
        except Exception as e:
            errors.append("Beam {}: {}".format(created+skipped, str(e)[:80]))
            skipped += 1

    txn.Commit()
except Exception as e:
    txn.RollbackIfNotCommitted()
    print("TRANSACTION ERROR: " + str(e))
    raise

# ============================================================
# STEP 7: VERIFY
# ============================================================
print("\n=== RESULTS ===")
print("Created : {}".format(created))
print("Skipped : {}".format(skipped))
if errors:
    print("Errors  : {}".format(len(errors)))
    for e in errors[:5]:
        print("  " + e)

# Quick verification
beams_all = DB.FilteredElementCollector(doc)\
    .OfCategory(DB.BuiltInCategory.OST_StructuralFraming)\
    .OfClass(DB.FamilyInstance).ToElements()

level_z_m = target_level.Elevation * 0.3048
new_beams = []
for b in beams_all:
    try:
        if FAMILY_NAME not in b.Symbol.Family.Name: continue
        loc = b.Location
        if isinstance(loc, DB.LocationCurve):
            z_m = loc.Curve.GetEndPoint(0).Z * 0.3048
            if level_z_m - 0.2 < z_m <= level_z_m:
                new_beams.append(b)
    except:
        pass

type_check = Counter(
    b.Symbol.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
    for b in new_beams
)
print("\nVerification — beams at {}:".format(TARGET_LEVEL_NAME))
print("  Total: {}".format(len(new_beams)))
for t, cnt in sorted(type_check.items()):
    print("  {}: {}".format(t, cnt))
