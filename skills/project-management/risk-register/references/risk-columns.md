# Risk register columns — alias mapping & scoring

`score_risks.py` tự dò cột theo tên (không phân biệt hoa/thường).

| Canonical | Header thường gặp / common headers |
|-----------|-------------------------------------|
| `id` | Risk ID, Risk, Ref, No, Number |
| `description` | Description, Risk Description, Title, Event, Name |
| `category` | Category, Type, Area, Risk Category |
| `owner` | Owner, Risk Owner, Assigned To, Responsible |
| `probability` | Probability, Likelihood, Prob, P |
| `impact` | Impact, Consequence, Severity, I |
| `status` | Status, State |
| `review_date` | Review Date, Review, Next Review, Due, Review By |
| `mitigation` | Mitigation, Response, Action, Treatment, Control |

## Thang probability / impact
Chấp nhận số **1–5** hoặc từ khoá (không phân biệt hoa/thường):

| Điểm | Từ khoá |
|------|---------|
| 1 | Very Low, VL |
| 2 | Low, Minor, Unlikely |
| 3 | Medium, Moderate, Possible |
| 4 | High, Major, Likely |
| 5 | Very High, Critical, Severe, Almost Certain |

## RAG (từ điểm P×I)
- `RED` ≥ 15 — ưu tiên xử lý, đưa lên báo cáo/họp.
- `AMBER` 8–14 — theo dõi, có kế hoạch ứng phó.
- `GREEN` < 8 — chấp nhận / giám sát định kỳ.

## Quy ước / conventions
- **Đóng / closed**: status ∈ {closed, retired, expired, realised}.
- **Overdue review**: `review_date` < mốc so hạn **và** rủi ro chưa đóng.

## Ngày / date formats
`YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`, `YYYY/MM/DD`, `DD-Mon-YYYY`, `MM/DD/YY`.
