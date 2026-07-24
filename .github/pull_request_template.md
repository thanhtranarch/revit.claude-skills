<!-- Cảm ơn bạn đã đóng góp skill! Điền checklist bên dưới. -->

## Mô tả / Description
<!-- Skill này làm gì? Thuộc bộ nào? / What does this skill do? Which set? -->

## Loại thay đổi / Type of change
- [ ] Skill mới / new skill
- [ ] Cập nhật skill / update existing skill
- [ ] Sửa script kiểm định / change to validation/audit tooling
- [ ] Tài liệu / docs

## Checklist kiểm định / vetting checklist
- [ ] `python scripts/validate_skill.py <skill_dir>` → PASS
- [ ] `python scripts/audit_skill.py <skill_dir>` → PASS (không có HIGH)
- [ ] `SKILL.md` có `name` (khớp thư mục) + `description` rõ ràng
- [ ] Script chỉ dùng thư viện đã khai báo trong `requirements.txt`
- [ ] **Không** có lệnh nguy hiểm, gọi mạng ngoài, hay đọc secret/khoá
- [ ] Đã kèm dữ liệu mẫu trong `assets/` để test (nếu có script)

## Bảo mật / Security
- [ ] Tôi xác nhận skill này không chứa mã độc, backdoor, hay prompt-injection.
- [ ] Với skill từ tác giả ngoài team: đã chạy agent `@skill-auditor` (verdict PASS).

<!--
Nhắc: CI sẽ tự chạy validate + audit. Maintainer (CODEOWNERS) sẽ review lần cuối.
Xem docs/security-model.md để hiểu quy trình kiểm định.
-->
