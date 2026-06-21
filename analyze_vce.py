"""
Script phân tích + test parse file .vce thực.
Chạy: python analyze_vce.py
Sau khi dùng, có thể xóa file này.
"""

import os
import sys
import struct
import zipfile

sys.path.insert(0, os.path.dirname(__file__))

VCE_FILES = [
    r"1. ECBA\ECBA_Part1.vce",
    r"1. ECBA\ECBA_Part2.vce",
]


def show_binary_info(path: str):
    with open(path, "rb") as f:
        raw = f.read()

    print(f"\n{'='*60}")
    print(f"File: {path}")
    print(f"Size: {len(raw):,} bytes")
    print(f"Magic (hex): {raw[:16].hex()}")
    print(f"Magic (repr): {repr(raw[:16])}")

    # Kiểm tra ZIP
    if raw[:4] == b"PK\x03\x04":
        print(">>> Đây là file ZIP!")
        try:
            with zipfile.ZipFile(path) as zf:
                for name in zf.namelist():
                    info = zf.getinfo(name)
                    print(f"  {name}  ({info.file_size:,} bytes)")
                    if name.lower().endswith(".xml"):
                        data = zf.read(name).decode("utf-8", errors="replace")
                        print(f"  --- XML preview (500 chars) ---")
                        print(data[:500])
        except Exception as e:
            print(f"  Lỗi đọc ZIP: {e}")
    else:
        print(">>> Không phải ZIP thuần — kiểm tra ZIP ẩn...")
        zip_offset = raw.find(b"PK\x03\x04")
        if zip_offset > 0:
            print(f">>> Tìm thấy ZIP tại offset {zip_offset}")
        else:
            print(">>> Không có ZIP. Đây là binary thuần.")

        # Thử tìm UTF-16LE strings
        print("\nTìm UTF-16LE strings (dài ≥ 10 ký tự):")
        count = 0
        i = 0
        while i < min(len(raw) - 4, 200000) and count < 30:
            (length,) = struct.unpack_from("<H", raw, i)
            if 10 <= length <= 1000:
                end = i + 2 + length * 2
                if end <= len(raw):
                    chunk = raw[i + 2: end]
                    try:
                        s = chunk.decode("utf-16-le")
                        printable = sum(1 for c in s if 0x20 <= ord(c) < 0x7F or ord(c) > 0xFF)
                        if printable / len(s) > 0.55:
                            print(f"  [offset={i}, len={length}]: {repr(s[:80])}")
                            count += 1
                            i = end
                            continue
                    except UnicodeDecodeError:
                        pass
            i += 1
        if count == 0:
            print("  Không tìm thấy UTF-16LE strings rõ ràng.")
            print("  Thử 50 bytes đầu dạng UTF-8:")
            print("  " + repr(raw[:50].decode("utf-8", errors="replace")))

    # Test parser thực tế
    print(f"\n--- Test parse_vce() ---")
    try:
        from src.vce_parser import parse_vce, get_domains
        questions = parse_vce(path)
        print(f"OK: {len(questions)} câu hỏi")
        domains = get_domains(questions)
        print(f"Domains: {domains}")
        if questions:
            q = questions[0]
            print(f"\nCâu 1:")
            print(f"  Text: {q.text[:120]}")
            print(f"  Options: {q.options}")
            print(f"  Correct: {q.correct}")
            print(f"  Domain: {q.domain}")
    except Exception as e:
        print(f"FAIL: {e}")


if __name__ == "__main__":
    for vce in VCE_FILES:
        if os.path.exists(vce):
            show_binary_info(vce)
        else:
            print(f"\nKhông tìm thấy: {vce}")
    print("\nHoàn thành phân tích.")
