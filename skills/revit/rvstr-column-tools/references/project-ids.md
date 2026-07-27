# Project Element IDs — CXL-DPA (Document: CXL-DPA-M3-AR-H2C-ZZ-0001)

> Cập nhật: Session tháng 4/2026
> Lưu ý: IDs có thể thay đổi nếu model được recreate. Luôn verify trước khi dùng.

## Dimension Types
| Name | ID |
|---|---|
| DPA-DIM-2.5mm Check | **5408676** |
| DPA-DIM-2.5mm (261) | 261 |
| DPA-DIM-2.5mm (187755) | 187755 |
| DPA-DIM-2.0mm (248144) | 248144 |
| DPA-DIM-2.0mm (249448) | 249448 |
| DPA-DIM-1.5mm (248296) | 248296 |
| DPA-DIM-1.5mm (249554) | 249554 |
| PLAN - FFL_SCALE_100DN | 21437 |

## Wall Types (thường dùng)
| Name | ID |
|---|---|
| RC500A | (detect dynamically) |
| Ex_Plaster_Skimcoat_5 | **6594479** |
| AAC160F (5+150+5) | (detect dynamically) |
| DPA_CW_WITH CAPPING | (detect dynamically) |

## Column Family
| Name | Category |
|---|---|
| DPA_SC_COLUMN_RECTANGULAR | OST_StructuralColumns |

### Column Types (500mm series)
| Type Name | ID |
|---|---|
| 500mm X 2000mm | 6602890 |
| 500mm X 2200mm | 6602892 |
| 500mm X 2250mm | 6602894 |
| 500mm X 2300mm | 6602896 |
| 500mm X 2500mm | 6602898 |
| 500mm X 2600mm | 6602900 |
| 500mm X 2800mm | 6602902 |
| 500mm X 3000mm | 6602904 |
| 500mm X 3100mm | 6602906 |
| 500mm X 3150mm | 6602908 |
| 500mm X 3200mm | 6602910 |
| 500mm X 3450mm | 6602912 |
| 500mm X 3500mm | 6602914 |
| 500mm X 3650mm | 6602918 |
| 500mm X 3750mm | 6602920 |
| 500mm X 3900mm | 6602922 |
| 500mm X 4000mm | 6602924 |
| 500mm X 4350mm | 6602926 |
| 500mm X 4500mm | 6602928 |
| 500mm X 4700mm | 6602930 |

## Groups (LEVEL 1)
| Name | GroupType ID | Group Instance ID |
|---|---|---|
| CORE 1FL | 5443360 | (recreated each session) |
| WALL L1 | 6196488 | (check dynamically) |
| CORE 2FL | 6095734 | (check dynamically) |
| CORE 3FL | 5619579 | (check dynamically) |

## Levels
| Name | Notes |
|---|---|
| LEVEL 1 | Base level các column thực hiện |
| LOWER ROOF | Level của 4 ungrouped columns |

## Grid Summary
- **Vertical grids** (measure X): K1, K2, K3, K4, K5, K6, K7, K8, K10, K11, K12, K15, K16, K17, K18, K19, K22, K23, K24, K25, K26, K27, K28, K29*, K30, K31, K32, K33, K34, K35 (39 grids)
- **Horizontal grids** (measure Y): L1, L2, L3, L4, L5, L9, L10, L11, L12, L13, L15, L16, L17, L18, L19, L20, L21, L22, L23, L24, L25, L26, L27 (27 grids)

## Column Snap Results (sau session tháng 4/2026)
- 87 columns tổng cộng trong view `an_LEVEL 1 Copy 1`
- Tất cả X và Y snapped về 0 hoặc 5mm (tolerance 0.01mm)
- Residual tối đa: 0.000148mm (floating point noise — acceptable)
- 70 columns overlap 100% với RC500A walls (expected behavior)
- 1 column overlap 19.2% với DPA_CW_WITH CAPPING (cần kiểm tra)
