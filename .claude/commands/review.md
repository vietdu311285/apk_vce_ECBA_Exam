# /review — Code Review Tự động

## Kích hoạt
Gõ: `/review @[tên_file]` hoặc `/review` (review toàn bộ thay đổi gần nhất)

## Claude sẽ kiểm tra theo thứ tự ưu tiên

### 🔴 HIGH — Bắt buộc sửa
1. **Bugs nghiêm trọng**: Logic errors, null/None không xử lý, off-by-one
2. **Security**: SQL injection, hardcoded secrets, XSS, path traversal
3. **Data loss risk**: Xóa dữ liệu không có xác nhận, overwrite file không backup

### 🟡 MEDIUM — Nên sửa
4. **Performance**: N+1 queries, vòng lặp không cần thiết, memory leak
5. **Error handling**: Thiếu try/except, exception bị bỏ qua
6. **Code quality**: Hàm quá dài (>50 dòng), logic lồng nhau sâu >3 cấp

### 🟢 LOW — Tùy chọn
7. **Naming**: Tên biến/hàm không rõ nghĩa
8. **DRY**: Code lặp lại có thể tách thành hàm
9. **Tests**: Thiếu test cases quan trọng

## Output format
```
📋 REVIEW: src/[filename].py
──────────────────────────────
🔴 HIGH [line X]: [mô tả vấn đề]
   → Fix: [đề xuất cụ thể]

🟡 MEDIUM [line Y]: [mô tả vấn đề]  
   → Fix: [đề xuất cụ thể]

✅ Tổng kết: X issues HIGH, Y issues MEDIUM
```

## Lưu ý
- Chỉ báo cáo issues THỰC SỰ quan trọng
- Bỏ qua style nếu đã có linter (flake8, eslint)
- Tập trung vào correctness và security trước
