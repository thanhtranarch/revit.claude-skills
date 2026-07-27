# CAD Layer Patterns — Dự án Vinhomes Smart City (CXL)

## Pattern Layer Beam

### Dự án HH2C / HH1A / HH1B / HHA / HHB
```
XR_HH2C_Level {X}-Floor Plan$0$S-_SUB-BEAM_H---
XR_HH1A_Level {X}-Floor Plan$0$S-_SUB-BEAM_H---
```
Trong đó `{X}` là số tầng.

### Cách tìm layer beam tự động
```python
import_cat = target_instance.Category
beam_layers = []
for sc in import_cat.SubCategories:
    name = getattr(sc, 'Name', '')
    if 'SUB-BEAM' in name.upper() or ('BEAM' in name.upper() and 'H---' in name):
        beam_layers.append((name, sc))
        
print("Beam layers found:")
for name, sc in beam_layers:
    print("  " + name)
```

## Các Layer Khác Thường Gặp

| Layer | Nội dung |
|-------|---------|
| `S-_SUB-SLAB_----` | Slab outline |
| `S-_SUB-SLAB_T---` | Slab thickness annotation |
| `S-_GEN-SYM-_D---` | Section/detail symbols |
| `S-_GEN-DIM-_----` | Dimensions |
| `S-_GEN-TEXT_T2--` | Text annotations |
| `DCE_SUB-COLN_S---` | Column section |
| `DCE_SUB-COLN_T---` | Column tag |
| `DCE_GoiDam` | Beam tag/annotation |
| `DCE_KT` | Dimension annotations |
| `DCE_TenNhip` | Span name annotation |

## Naming Convention File CAD — HH2C

| Tầng | Pattern tìm kiếm |
|------|----------------|
| 2 | `FP02` |
| 3 | `FP03` |
| 4 | `FP04` |
| 5–7, 10–12, 15–17, 20–22 | `FP05` (typical) |
| 8, 13, 18 | `FP08` |
| 9, 14, 19 | `FP09` |
| 23 | `FP23` |
| 24 | `FP24` |
| 25, 27, 30, 32 | `FP25` |
| 28, 33 | `FP28` |
| 29 | `FP29` |
| 34 | `FP34` |
| 35–37, 40–41 | `FP35` |
| 38 | `FP38` |
| 39 | `FP39` |
| 42 | `FP42` |
| 43 | `FP43` |
| 44 | `FP46 (44th)` |
| 45 | `FP45` |
| 46 | `FP46` |
| LMR | `FPLR` |
| Roof | `FPRF` |

## Level Names trong Revit Model

```
LEVEL 1  = EL. ±0.000
LEVEL 2  = EL. +4.200m
LEVEL 3  = EL. +8.400m
LEVEL 4  = EL. +11.650m
LEVEL 5+ = +3.250m mỗi tầng (typical)
```
