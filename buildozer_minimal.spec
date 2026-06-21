[app]
title = ECBA Minimal
package.name = ecbaminimal
package.domain = com.ecbaminimal
version = 0.1

source.main = main_minimal.py
source.dir = .
source.include_exts = py,png

requirements = python3,kivy,kivymd

icon.filename = assets/icon.png
orientation = portrait

android.minapi = 21
android.api = 31
android.ndk = 25b
android.accept_sdk_license = True
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0
