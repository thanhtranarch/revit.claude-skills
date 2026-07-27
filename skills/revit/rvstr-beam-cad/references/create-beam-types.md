# Tạo Beam Types trong M_Concrete-Rectangular Beam

## Kiểm tra types đã có

```python
symbols = DB.FilteredElementCollector(doc).OfClass(DB.FamilySymbol).ToElements()
beam_types = [s for s in symbols if s.Family.Name == 'M_Concrete-Rectangular Beam']

existing_names = set()
for t in beam_types:
    name = t.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
    b_mm = round(t.LookupParameter('b').AsDouble() * 304.8)
    h_mm = round(t.LookupParameter('h').AsDouble() * 304.8)
    existing_names.add(name)
    print("{}: b={}mm h={}mm".format(name, b_mm, h_mm))
```

## Tạo type mới bằng cách Duplicate

```python
MM_TO_FT = 1.0 / 304.8

# Danh sách type cần tạo: (b_mm, h_mm, type_name)
beam_sizes = [
    (200, 400,  "200 x 400mm"),
    (200, 500,  "200 x 500mm"),
    (250, 400,  "250 x 400mm"),
    (250, 500,  "250 x 500mm"),
    (250, 600,  "250 x 600mm"),
    (250, 700,  "250 x 700mm"),
    (300, 500,  "300 x 500mm"),
    (300, 600,  "300 x 600mm"),
    (300, 700,  "300 x 700mm"),
    (300, 800,  "300 x 800mm"),
    (350, 700,  "350 x 700mm"),
    (350, 800,  "350 x 800mm"),
    (400, 700,  "400 x 700mm"),
    (400, 800,  "400 x 800mm"),
    (400, 900,  "400 x 900mm"),
    (400, 1000, "400 x 1000mm"),
    (500, 1000, "500 x 1000mm"),
    (500, 1200, "500 x 1200mm"),
    (600, 1200, "600 x 1200mm"),
]

# Lấy template (bất kỳ type đã có)
template_type = beam_types[0]

created, skipped, errors = [], [], []

t_tx = DB.Transaction(doc, "Create Beam Types")
t_tx.Start()
try:
    for (b_mm, h_mm, type_name) in beam_sizes:
        if type_name in existing_names:
            skipped.append(type_name)
            continue
        try:
            new_type = template_type.Duplicate(type_name)
            new_type.LookupParameter('b').Set(b_mm * MM_TO_FT)
            new_type.LookupParameter('h').Set(h_mm * MM_TO_FT)
            created.append(type_name)
        except Exception as e:
            errors.append("{}: {}".format(type_name, e))
    t_tx.Commit()
except Exception as e:
    t_tx.RollbackIfNotCommitted()
    print("ERROR: " + str(e))

print("Created: {}".format(len(created)))
print("Skipped: {}".format(len(skipped)))
for e in errors:
    print("ERROR: " + e)
```

## Lưu ý

- Parameter `b` = chiều rộng (width), `h` = chiều cao (height), đơn vị **feet** trong Revit API
- Naming convention: `"{b} x {h}mm"` — ví dụ: `"300 x 600mm"`
- Nếu family chưa có trong model, cần load từ library trước:
  ```python
  # Load family từ đường dẫn
  fam_path = r"C:\ProgramData\Autodesk\RVT 2023\Libraries\...\M_Concrete-Rectangular Beam.rfa"
  result = doc.LoadFamily(fam_path)
  ```
