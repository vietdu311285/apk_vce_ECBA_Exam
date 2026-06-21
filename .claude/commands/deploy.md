# /deploy — Checklist Deploy Ứng dụng

## Kích hoạt
Gõ: `/deploy` trước khi deploy lên production

## ⚠️ QUAN TRỌNG
Nếu bất kỳ bước nào FAIL → Claude sẽ BÁO LỖI và DỪNG, không tiếp tục deploy

## Checklist tự động

### 1️⃣ Code Quality
- [ ] Không có lỗi syntax: `python -m py_compile src/*.py`
- [ ] Lint pass: `flake8 src/` hoặc `npm run lint`
- [ ] Type check: `mypy src/` hoặc `npm run typecheck`

### 2️⃣ Tests
- [ ] Tất cả tests pass: `pytest` hoặc `npm test`
- [ ] Coverage tối thiểu 70%: `pytest --cov=src`

### 3️⃣ Security
- [ ] Không có secrets trong code: `git grep -i "password\|api_key\|secret"`
- [ ] Dependencies không có CVE nghiêm trọng: `pip audit` / `npm audit`
- [ ] File `.env` không trong git: `git status .env`

### 4️⃣ Environment
- [ ] Tất cả ENV vars đã set trên production
- [ ] Database migrations đã chạy
- [ ] Health check endpoint hoạt động

### 5️⃣ Backup
- [ ] Database đã backup trước deploy
- [ ] Có kế hoạch rollback nếu lỗi

## Lệnh deploy (cập nhật theo dự án)
```bash
# Ví dụ deploy lên server
git push origin main
ssh user@server "cd /app && git pull && pip install -r requirements.txt && sudo systemctl restart myapp"
```
