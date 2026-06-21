[app]
title = ECBA Exam Simulator
package.name = ecbaexam
package.domain = com.ecbasim
version = 1.0.0

source.main = main.py
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,vce

requirements = python3,kivy,kivymd,pillow

icon.filename = assets/icon.png
orientation = portrait

android.minapi = 21
android.api = 31
android.ndk = 25b
android.accept_sdk_license = True
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.archs = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 0
