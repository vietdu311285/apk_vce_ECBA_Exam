# ECBA Exam Simulator

Ứng dụng Android đọc file `.vce` để ôn thi chứng chỉ **ECBA** (Entry Certificate in Business Analysis — PMI).

## Tính năng

| Tính năng | Mô tả |
|-----------|-------|
| Thi thử có đếm giờ | Mô phỏng đúng điều kiện thi: 50 câu / 150 phút |
| Ôn tập | Xem đáp án + giải thích ngay sau mỗi câu |
| Thi theo domain | Lọc câu hỏi theo từng domain ECBA |
| Lịch sử làm bài | Xem 5 lần thi gần nhất, có điểm và kết quả |
| Review câu sai | Xem lại câu sai + giải thích sau khi thi |

---

## Hướng dẫn nhanh

### Bước 1 — Chuẩn bị file .vce

Đặt file `.vce` ECBA của bạn vào thư mục `tests/sample.vce` (để test) hoặc để trên điện thoại sau khi cài APK.

### Bước 2 — Chạy thử trên Windows (Desktop)

```bash
# Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate

# Cài thư viện
pip install -r requirements.txt

# Chạy app
python main.py
```

> App sẽ mở cửa sổ 400×800 px giống màn hình điện thoại.

### Bước 3 — Test parser với file .vce thực

```bash
python -m pytest tests/ -v
```

Nếu có file `.vce` thực, copy vào `tests/sample.vce` — test case `test_real_vce_file` sẽ tự chạy.

### Bước 4 — Build APK (GitHub Actions, không cần cài gì thêm)

1. **Tạo GitHub repo** (private hoặc public):
   ```
   git init
   git add .
   git commit -m "Initial ECBA exam simulator"
   git remote add origin https://github.com/<username>/<repo>.git
   git push -u origin main
   ```

2. **Đợi build tự động** (~20–30 phút lần đầu):
   - Vào tab **Actions** trên GitHub
   - Chọn workflow **"Build ECBA APK"**
   - Đợi dấu tích xanh ✓

3. **Tải APK**:
   - Click vào run vừa xong
   - Mục **Artifacts** → Download `ecba-exam-apk.zip`
   - Giải nén → có file `.apk`

### Bước 5 — Cài APK lên Android

```
1. Copy file .apk vào điện thoại
   (qua USB, Google Drive, Telegram, v.v.)

2. Bật "Cài từ nguồn không xác định":
   - Android 8.0+: Settings → Apps → [File Manager bạn dùng] → Install unknown apps → Cho phép
   - Android 7 trở xuống: Settings → Security → Unknown sources → Bật

3. Mở File Manager, tìm file .apk → Nhấn cài đặt

4. Mở app "ECBA Exam Simulator" → Chọn file .vce → Bắt đầu!
```

> APK tương thích **Android 5.0+ (API 21)** — hầu hết điện thoại Android hiện nay.

---

## Cấu trúc dự án

```
├── main.py                  # Entry point Kivy app
├── buildozer.spec           # Cấu hình build APK
├── requirements.txt
├── .github/workflows/
│   └── build_apk.yml        # GitHub Actions CI/CD
├── src/
│   ├── vce_parser.py        # Parse file .vce → câu hỏi
│   ├── exam_engine.py       # Timer, shuffle, chấm điểm
│   ├── storage.py           # Lưu lịch sử JSON
│   └── ui/
│       ├── home_screen.py   # Màn hình chủ
│       ├── exam_screen.py   # Màn hình thi
│       └── result_screen.py # Kết quả
├── assets/
│   └── icon.png             # Icon app
└── tests/
    ├── test_vce_parser.py
    └── sample.vce           # File .vce mẫu (bạn cung cấp)
```

---

## Điều chỉnh khi có file .vce thực

Nếu parser chưa đọc đúng file `.vce` của bạn:

1. Đổi tên file `.vce` → `.zip` rồi giải nén
2. Xem cấu trúc XML bên trong
3. Cập nhật `src/vce_parser.py`:
   - Sửa tên tag XML trong `_try_avanset_schema()` cho khớp
   - Chạy lại `python -m pytest tests/ -v` để verify

---

## Tiêu chí đạt ECBA

- **Tổng câu**: 50 câu trắc nghiệm
- **Thời gian**: 150 phút (2 giờ 30 phút)  
- **Điểm đạt**: ≥ 70% (35/50 câu đúng)
- **Domains**: Business Analysis Planning, Elicitation, Requirements Life Cycle Management, Strategy Analysis, Requirements Analysis & Design Definition, Solution Evaluation
