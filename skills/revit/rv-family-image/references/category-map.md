# Image Object → Revit Category Map

Use this table during Stage 2 (image analysis) to determine the correct
Revit category for the detected object.

## Furniture & Seating

| Object | Category | host_type |
|---|---|---|
| Sofa, couch | Furniture | non-hosted |
| Armchair, lounge chair | Furniture | non-hosted |
| Dining chair, side chair | Furniture | non-hosted |
| Windsor chair, bentwood chair | Furniture | non-hosted |
| Office chair | Furniture | non-hosted |
| Bar stool | Furniture | non-hosted |
| Coffee table | Furniture | non-hosted |
| Dining table | Furniture | non-hosted |
| Desk | Furniture | non-hosted |
| Bookshelf, bookcase | Furniture | non-hosted |
| Wardrobe, closet | Casework | non-hosted |
| Kitchen cabinet | Casework | wall-hosted |
| Bed | Furniture | non-hosted |
| Bench | Furniture | non-hosted |
| Ottoman, footstool | Furniture | non-hosted |

## Fixtures & Sanitary

| Object | Category | host_type |
|---|---|---|
| Washbasin, lavatory sink | Plumbing Fixtures | wall-hosted or non-hosted |
| Toilet, WC | Plumbing Fixtures | floor-hosted |
| Bathtub | Plumbing Fixtures | floor-hosted |
| Shower tray | Plumbing Fixtures | floor-hosted |
| Urinal | Plumbing Fixtures | wall-hosted |
| Kitchen sink | Plumbing Fixtures | non-hosted |

## Lighting

| Object | Category | host_type |
|---|---|---|
| Pendant light | Lighting Fixtures | ceiling-hosted |
| Ceiling lamp | Lighting Fixtures | ceiling-hosted |
| Wall sconce | Lighting Fixtures | wall-hosted |
| Floor lamp | Lighting Fixtures | non-hosted |
| Table lamp | Lighting Fixtures | non-hosted |
| Track light | Lighting Fixtures | ceiling-hosted |

## Other

| Object | Category | host_type |
|---|---|---|
| Decorative object | Generic Models | non-hosted |
| Plant, pot | Specialty Equipment | non-hosted |
| Appliance | Mechanical Equipment | non-hosted |
| TV, monitor | Specialty Equipment | non-hosted |

## Dimension Defaults by Category

Use these as fallback dimensions when not determinable from the image:

| Category | W (mm) | D (mm) | H (mm) |
|---|---|---|---|
| Sofa 3-seat | 2100 | 900 | 850 |
| Sofa 2-seat | 1600 | 900 | 850 |
| Armchair | 850 | 850 | 850 |
| Dining chair | 450 | 500 | 900 |
| Coffee table | 1200 | 600 | 450 |
| Dining table (4p) | 1400 | 800 | 750 |
| Washbasin wall | 600 | 450 | 200 |
| Single bed | 1000 | 2100 | 600 |
| Double bed | 1600 | 2100 | 600 |
