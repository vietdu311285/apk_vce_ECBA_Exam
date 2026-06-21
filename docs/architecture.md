# Kiến trúc Hệ thống — [Tên Dự Án]

## Tổng quan
[Mô tả ngắn: ứng dụng này làm gì, phục vụ ai]

## Sơ đồ kiến trúc
```
[Client / Browser]
       ↓
[API Layer - FastAPI/Flask]
       ↓
[Business Logic - Services]
       ↓
[Data Layer - Database]
```

## Các thành phần chính

### Frontend (nếu có)
- Công nghệ: [React / HTML / etc.]
- Đường dẫn: `src/frontend/`
- Chức năng: [mô tả]

### Backend / API
- Công nghệ: [FastAPI / Flask / Django]
- Đường dẫn: `src/api/`
- Endpoints chính:
  - `GET /api/items` — Lấy danh sách
  - `POST /api/items` — Tạo mới
  - `PUT /api/items/{id}` — Cập nhật
  - `DELETE /api/items/{id}` — Xóa

### Database
- Công nghệ: [PostgreSQL / SQLite]
- Schema: `docs/schema.sql`
- Migrations: `migrations/`

## Data Flow
1. User gửi request từ browser
2. API nhận và validate input
3. Service layer xử lý business logic
4. Database lưu/đọc dữ liệu
5. Trả response về client

## Security
- Authentication: [JWT / Session / etc.]
- Authorization: [Role-based / etc.]
- Data validation: [Pydantic / Zod / etc.]

## Môi trường
| Môi trường | URL | Database |
|-----------|-----|----------|
| Development | localhost:8000 | SQLite local |
| Staging | staging.example.com | PostgreSQL |
| Production | example.com | PostgreSQL |
