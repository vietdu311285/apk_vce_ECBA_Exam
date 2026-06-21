# Project: [TÊN DỰ ÁN CỦA BẠN]

## 🛠️ Stack & Môi trường
- Language: Python 3.11 / TypeScript / JavaScript
- Framework: FastAPI / Next.js / Flask
- Database: PostgreSQL / SQLite / MongoDB
- Package manager: pip / npm / pnpm

## 📁 Cấu trúc thư mục
- `src/` — Source code chính
- `tests/` — Unit tests và integration tests
- `docs/` — Tài liệu dự án
- `scripts/` — Scripts hỗ trợ

## ⚙️ Lệnh thường dùng
```bash
# Python
python -m venv venv         # Tạo môi trường ảo
source venv/bin/activate    # Kích hoạt (Mac/Linux)
venv\Scripts\activate       # Kích hoạt (Windows)
pip install -r requirements.txt
python main.py

# Node.js
npm install
npm run dev
npm run build
npm test
```

## 📏 Quy tắc code (BẮT BUỘC)
1. Dùng type hints cho Python (def func(x: int) -> str:)
2. Comment bằng tiếng Việt cho phần logic phức tạp
3. Đặt tên biến rõ ràng: `user_name` thay vì `un`
4. Hàm tối đa 50 dòng, tách nhỏ nếu cần
5. Xử lý lỗi: luôn dùng try/except với thông báo rõ ràng

## ✅ Làm
- Viết docstring cho mọi hàm/class
- Validate input trước khi xử lý
- Log lỗi với đủ thông tin để debug

## ❌ Không làm
- Hard-code passwords, API keys vào code
- Bỏ qua exception (except: pass)
- Magic numbers không giải thích (dùng constants)

## 🐛 Khi gặp lỗi
1. Copy toàn bộ error message và stack trace
2. Tag file liên quan: @src/main.py
3. Dùng lệnh: /debug [mô tả lỗi]

## 📝 Environment variables
- Xem file `.env.example` để biết cần những biến gì
- TUYỆT ĐỐI không commit file `.env` thật lên Git
- Copy `.env.example` → `.env` và điền giá trị thật

## 🔗 Tài liệu tham khảo
- API docs: [link docs nếu có]
- Architecture: @docs/architecture.md
- Conventions: @docs/conventions.md
