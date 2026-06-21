[app]

# Tên hiển thị trên màn hình Android
title = ECBA Exam Simulator

# Package name (phải là domain.appname dạng chữ thường, không dấu)
package.name = ecbaexam
package.domain = com.ecbasim

# Phiên bản app
version = 1.0.0

# File entry point
source.main = main.py

# Thư mục source (bao gồm src/)
source.include_exts = py,png,jpg,jpeg,json,vce,xml,ttf
source.dir = .

# Thư viện Python cần thiết
requirements = python3==3.11.0,kivy==2.3.0,kivymd==1.2.0,pillow

# Icon (thay bằng file icon.png của bạn)
icon.filename = assets/icon.png

# Màn hình mặc định: portrait
orientation = portrait

# Android API
android.minapi = 21
android.api = 33
android.ndk = 25b

# Quyền truy cập file
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# Arch hỗ trợ (arm64-v8a cho máy mới, armeabi-v7a cho máy cũ)
android.archs = arm64-v8a, armeabi-v7a

# Cho phép backup dữ liệu
android.allow_backup = True

# Fullscreen
fullscreen = 0

[buildozer]

# Thư mục log
log_level = 2

# Không dùng sudo khi cài (dùng trong GitHub Actions)
warn_on_root = 1
