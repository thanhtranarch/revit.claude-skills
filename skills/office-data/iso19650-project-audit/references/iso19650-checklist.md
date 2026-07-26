# ISO 19650 — Checklist kiểm tra tuân thủ dự án / project conformance checklist

Ghi chú tham chiếu cho `audit_iso19650_project.py`. Mã dưới đây theo **UK BIM
Framework / BS EN ISO 19650-2**; **luôn ưu tiên bảng mã trong BEP/EIR của dự án**
(tuỳ biến bằng `--rules`).

## 1. Trạng thái CDE / CDE states
Container đi qua 4 trạng thái trong Common Data Environment:

| State | Ý nghĩa | Suitability điển hình | Revision |
|-------|---------|-----------------------|----------|
| **WIP** (Work in Progress) | Đang làm, chưa chia sẻ | `S0` | `Pxx` |
| **Shared** | Chia sẻ để phối hợp/thông tin (chưa hợp đồng) | `S1`–`S7` | `Pxx` |
| **Published** | Đã duyệt, dùng chính thức (hợp đồng) | `A1`–`An`, `B1`–`Bn`, `CR` | `Cxx` |
| **Archived** | Lưu vết phiên bản cũ | — | — |

## 2. Mã suitability / status codes
| Nhóm | Mã | Ý nghĩa (rút gọn) |
|------|----|-------------------|
| WIP | `S0` | Initial / WIP |
| Shared | `S1` | Suitable for coordination |
| | `S2` | Suitable for information |
| | `S3` | Suitable for review & comment |
| | `S4` | Suitable for stage approval |
| | `S6` | Suitable for PIM authorization |
| | `S7` | Suitable for AIM authorization |
| Published | `A1…An` | Authorized & accepted |
| | `B1…Bn` | Partially authorized (có comment) |
| | `CR` | As-constructed record |
| For info | `D1…D4` | For information / handover data |

> `S5` và một số mã khác thay đổi giữa các phiên bản/tổ chức — chỉnh
> `suitability_allowed` trong `--rules` theo BEP dự án.

## 3. Mã revision / revision codes
- **`Pxx`** — preliminary (giai đoạn WIP/Shared), vd `P01`, `P02`, `P01.1`.
- **`Cxx`** — contractual (đã Published), vd `C01`, `C02`.
- Regex mặc định: `^[PC][0-9]{2}(\.[0-9]{1,2})?$`.

## 4. Metadata bắt buộc mỗi container / required container metadata
`name` (mã container), `title`, `originator`, `suitability`, `revision`, `date`
(ISO 8601 `YYYY-MM-DD`). Thiếu bất kỳ trường nào → chưa đạt.

## 5. Skill này kiểm TỰ ĐỘNG gì / what the tool checks
1. **Metadata đầy đủ** — 6 trường trên không trống.
2. **Tên có cấu trúc** — đủ ≥6 trường ISO 19650 (chi tiết field: dùng
   `iso19650-naming-check`).
3. **Suitability hợp lệ** — thuộc danh mục.
4. **Revision hợp lệ** — đúng `Pxx/Cxx`.
5. **Date ISO 8601**.
6. **Nhất quán trạng thái** — Published⇒A/B/CR & `Cxx`; Shared⇒S1–S7 & `Pxx`;
   WIP⇒S0.
7. (Tuỳ chọn) **Đối chiếu MIDP** — `--expected midp.csv`: container kỳ vọng nào
   chưa có trong register.

## 6. Cần người/BEP review (ngoài phạm vi tự động) / needs human review
- Cấu trúc thư mục & phân quyền CDE thực tế.
- Ma trận trách nhiệm **TIDP/MIDP**, lịch phát hành, mốc thông tin.
- **LOIN/LOD** — mức độ thông tin có đạt yêu cầu giai đoạn không.
- Federation strategy, đặt tên volume/system theo BEP.
- Tính đúng đắn *nội dung* (chỉ kiểm được *metadata*, không kiểm chất lượng model).
