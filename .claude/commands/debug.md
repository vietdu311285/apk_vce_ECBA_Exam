# /debug — Trợ lý Debug Lỗi

## Kích hoạt
Gõ: `/debug [mô tả lỗi hoặc paste error message]`

## Quy trình Claude sẽ thực hiện

### Bước 1 — Phân tích lỗi
- Đọc error message và stack trace
- Xác định loại lỗi: syntax / runtime / logic / import

### Bước 2 — Tìm nguyên nhân (top 3)
- Liệt kê 3 nguyên nhân có thể nhất theo xác suất
- Giải thích ngắn tại sao mỗi nguyên nhân có thể xảy ra

### Bước 3 — Đề xuất fix
- Fix cụ thể theo từng nguyên nhân
- Ưu tiên fix đơn giản nhất trước

### Bước 4 — Cách verify
- Cách kiểm tra xem đã fix chưa
- Test case cụ thể để chạy thử

## Output format
```
🔴 LỖI: [mô tả ngắn]
📁 File: [tên file và dòng]
🎯 Nguyên nhân: [nguyên nhân chính]
🔧 Fix:
  [code fix cụ thể]
✅ Verify: [cách kiểm tra]
🛡️ Prevention: [cách tránh lỗi tương tự]
```

## Ví dụ sử dụng
```
/debug
Error: ModuleNotFoundError: No module named 'requests'
File: src/api_client.py, line 3
```
