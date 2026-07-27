# Navisworks Clash XML — ghi chú cấu trúc / structure notes

Xuất từ Clash Detective → Report tab → **Report Type: XML**.

## Cây thẻ chính / main element tree
```
exchange
└─ batchtest                     (một lần chạy report)
   └─ clashtests
      └─ clashtest  @name        (một clash test, vd "STR vs MEP")
         └─ clashresults
            └─ clashresult  @name @status @distance @gridlocation
               └─ clashobjects
                  ├─ clashobject   (item thứ nhất)
                  │   └─ smarttags/smarttag/(name,value)
                  └─ clashobject   (item thứ hai)
```

## Thuộc tính hữu ích / useful attributes
- `clashresult@status`: `new | active | reviewed | approved | resolved`.
- `clashresult@distance`: khoảng cách xuyên (âm = chồng lấn).
- `clashresult@gridlocation`: vị trí lưới + level (nếu có gridsystem).
- `smarttag value`: tên/property của item — tuỳ chọn hiển thị khi xuất report.

## Lưu ý phiên bản / version notes
- Tên thẻ và thuộc tính có thể đổi nhẹ theo phiên bản Navisworks. Script
  `parse_clash.py` dùng `.iter()` nên bỏ qua khác biệt về thẻ bao ngoài.
- Nếu không thấy tên item, bật thêm cột property khi xuất report, hoặc chỉnh
  hàm `_text()` trong script để đọc đúng đường dẫn smarttag.
