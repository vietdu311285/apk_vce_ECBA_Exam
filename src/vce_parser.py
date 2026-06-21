"""
VCE file parser — đọc file .vce (Avanset binary hoặc ZIP/XML) → list[Question].

Avanset VCE là format binary độc quyền. Module này thử các chiến lược:
  1. ZIP/XML (một số tool tạo .vce dạng ZIP)
  2. ZIP ẩn trong binary (có binary header trước dữ liệu ZIP)
  3. Avanset binary — quét tìm chuỗi UTF-16LE (Windows-native format)
  4. Nếu vẫn thất bại → báo lỗi rõ ràng kèm hướng dẫn
"""

from __future__ import annotations

import struct
import zipfile
import io
import re
import xml.etree.ElementTree as ET
import base64
import logging
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)

ZIP_MAGIC = b"PK\x03\x04"


@dataclass
class Question:
    id: str
    domain: str                      # ECBA domain
    text: str
    options: list[str]               # nội dung A, B, C, D...
    correct: list[int]               # index 0-based đáp án đúng
    explanation: str
    question_type: Literal["single", "multi"] = "single"
    image_data: bytes | None = None


class VCEParseError(Exception):
    """Lỗi khi parse file .vce."""


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def parse_vce(file_path: str) -> list[Question]:
    """
    Đọc file .vce trả về danh sách câu hỏi.

    Raises:
        VCEParseError: định dạng không nhận ra hoặc parse thất bại
        FileNotFoundError: file không tồn tại
    """
    with open(file_path, "rb") as f:
        raw = f.read()

    logger.debug("File size: %d bytes, magic: %s", len(raw), raw[:4].hex())

    # Chiến lược 1: ZIP thuần
    if raw[:4] == ZIP_MAGIC:
        try:
            return _parse_zip_vce(io.BytesIO(raw))
        except Exception as e:
            logger.warning("ZIP parse thất bại: %s", e)

    # Chiến lược 2: tìm ZIP ẩn bên trong binary
    zip_offset = raw.find(ZIP_MAGIC)
    if zip_offset > 0:
        logger.debug("Tìm thấy ZIP tại offset %d", zip_offset)
        try:
            return _parse_zip_vce(io.BytesIO(raw[zip_offset:]))
        except Exception as e:
            logger.warning("ZIP ẩn parse thất bại: %s", e)

    # Chiến lược 3: Avanset binary VCE (UTF-16LE strings)
    questions = _parse_avanset_binary(raw)
    if questions:
        return questions

    # Chiến lược 4: quét text UTF-8 thô
    questions = _parse_text_fallback(raw)
    if questions:
        return questions

    raise VCEParseError(
        f"Không parse được file .vce. Magic bytes: {raw[:8].hex()}\n"
        "Hướng dẫn xử lý:\n"
        "  1. Cài Avanset Visual CertExam Suite trên Windows\n"
        "  2. Mở file .vce → Export sang PDF hoặc TXT\n"
        "  3. Dùng file export đó với app này\n"
        "Hoặc chạy analyze_vce.py để xem cấu trúc file."
    )


def get_domains(questions: list[Question]) -> list[str]:
    """Trả về danh sách domain unique, với 'Tất cả' ở đầu."""
    domains = sorted({q.domain for q in questions if q.domain})
    return ["Tất cả"] + domains


# ─────────────────────────────────────────────────────────────────────────────
# Chiến lược 1 & 2: ZIP/XML
# ─────────────────────────────────────────────────────────────────────────────

def _parse_zip_vce(buf: io.BytesIO) -> list[Question]:
    with zipfile.ZipFile(buf, "r") as zf:
        names = zf.namelist()
        logger.debug("ZIP contents: %s", names)
        xml_files = [n for n in names if n.lower().endswith(".xml")]
        if not xml_files:
            raise VCEParseError(f"Không có XML trong ZIP. Files: {names}")
        xml_data = zf.read(xml_files[0])
        root = ET.fromstring(xml_data)

    questions = _try_avanset_xml_schema(root) or _try_generic_xml_schema(root)
    if not questions:
        raise VCEParseError("Không nhận ra schema XML trong .vce")
    return questions


def _try_avanset_xml_schema(root: ET.Element) -> list[Question]:
    for tag in ("Question", "question", "Item", "item", "QUESTION"):
        els = root.findall(f".//{tag}")
        if els:
            return [_parse_xml_question(el, i) for i, el in enumerate(els)]
    return []


def _parse_xml_question(el: ET.Element, idx: int) -> Question:
    def txt(*tags: str) -> str:
        for t in tags:
            n = el.find(t)
            if n is not None and n.text:
                return n.text.strip()
        return ""

    q_id = el.get("id") or el.get("Id") or str(idx + 1)
    domain = txt("Domain", "domain", "Category", "Section", "section")
    text = txt("QuestionText", "Text", "Stem", "Body", "stem", "text")
    explanation = txt("Explanation", "Rationale", "rationale")

    options, correct = [], []
    for ans_tag in ("Answer", "Choice", "Option", "answer", "choice"):
        answers = el.findall(ans_tag)
        if answers:
            for i, ans in enumerate(answers):
                opt = (ans.text or "").strip() or ans.get("text", "") or ans.get("Text", "")
                options.append(opt)
                if any(ans.get(k, "").lower() in ("true", "1", "yes")
                       for k in ("correct", "isCorrect", "IsCorrect", "Correct")):
                    correct.append(i)
            break

    return Question(
        id=q_id,
        domain=domain or "General",
        text=text,
        options=options,
        correct=correct,
        explanation=explanation,
        question_type="multi" if len(correct) > 1 else "single",
    )


def _try_generic_xml_schema(root: ET.Element) -> list[Question]:
    best = max(list(root.iter()), key=lambda e: len(list(e)), default=None)
    if best is None or len(list(best)) < 2:
        return []
    results = []
    for i, child in enumerate(best):
        text = " ".join(t.strip() for t in child.itertext() if t.strip())
        if len(text) >= 20:
            results.append(Question(
                id=str(i + 1), domain="General", text=text[:600],
                options=[], correct=[], explanation="",
            ))
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Chiến lược 3: Avanset binary VCE
#
# Avanset lưu string dạng Pascal-string UTF-16LE:
#   [uint16 length_in_chars][UTF-16LE bytes]
# hoặc [uint32 length][UTF-16LE bytes]
# Câu hỏi thường xuất hiện theo cluster: question_text, answer1, answer2...
# ─────────────────────────────────────────────────────────────────────────────

_MIN_STR_LEN = 8      # ký tự tối thiểu để coi là string hợp lệ
_MAX_STR_LEN = 4000   # ký tự tối đa


def _extract_utf16le_strings(data: bytes) -> list[tuple[int, str]]:
    """Quét binary, trích xuất tất cả chuỗi UTF-16LE có độ dài hợp lý."""
    results: list[tuple[int, str]] = []
    i = 0
    while i < len(data) - 4:
        # Thử đọc uint16 làm độ dài string
        (length,) = struct.unpack_from("<H", data, i)
        if _MIN_STR_LEN <= length <= _MAX_STR_LEN:
            end = i + 2 + length * 2
            if end <= len(data):
                chunk = data[i + 2: end]
                try:
                    s = chunk.decode("utf-16-le")
                    # Kiểm tra là text đọc được (>60% ASCII printable)
                    printable = sum(1 for c in s if 0x20 <= ord(c) < 0x7F or ord(c) > 0xFF)
                    if printable / len(s) > 0.55:
                        results.append((i, s))
                        i = end
                        continue
                except UnicodeDecodeError:
                    pass
        i += 1
    return results


def _parse_avanset_binary(data: bytes) -> list[Question]:
    """Parse Avanset VCE binary format bằng cách quét UTF-16LE strings."""
    strings = _extract_utf16le_strings(data)
    logger.debug("Tìm thấy %d UTF-16LE strings", len(strings))

    if len(strings) < 4:
        return []

    # Lọc bỏ string quá ngắn (metadata headers)
    candidates = [(off, s) for off, s in strings if len(s) >= _MIN_STR_LEN]

    # Phân nhóm: mỗi câu hỏi thường gồm 5-8 string liên tiếp
    # (1 câu hỏi + 4 đáp án + 1 giải thích)
    questions = _cluster_into_questions(candidates)
    if questions:
        logger.info("Binary parse: tìm thấy %d câu hỏi", len(questions))
    return questions


def _cluster_into_questions(strings: list[tuple[int, str]]) -> list[Question]:
    """Nhóm strings lại thành câu hỏi dựa trên khoảng cách offset."""
    if not strings:
        return []

    # Tính khoảng cách giữa các string liên tiếp
    offsets = [s[0] for s in strings]
    gaps = [offsets[i + 1] - offsets[i] for i in range(len(offsets) - 1)]
    if not gaps:
        return []

    # Gap nhỏ = cùng nhóm câu hỏi, gap lớn = câu hỏi mới
    median_gap = sorted(gaps)[len(gaps) // 2]
    cluster_threshold = max(median_gap * 3, 50)

    groups: list[list[str]] = []
    current_group: list[str] = [strings[0][1]]

    for i in range(1, len(strings)):
        gap = strings[i][0] - strings[i - 1][0]
        if gap > cluster_threshold:
            if len(current_group) >= 2:
                groups.append(current_group)
            current_group = []
        current_group.append(strings[i][1])

    if len(current_group) >= 2:
        groups.append(current_group)

    logger.debug("Phân nhóm: %d nhóm từ %d strings", len(groups), len(strings))

    questions: list[Question] = []
    for i, group in enumerate(groups):
        if len(group) < 2:
            continue
        # Phần tử đầu tiên = câu hỏi, phần còn lại = đáp án + giải thích
        q_text = group[0]
        options = [s for s in group[1:] if len(s) > 3][:6]  # tối đa 6 đáp án

        questions.append(Question(
            id=str(i + 1),
            domain="General",
            text=q_text,
            options=options,
            correct=[],  # binary format không dễ xác định đáp án đúng
            explanation="",
            question_type="single",
        ))

    return questions


# ─────────────────────────────────────────────────────────────────────────────
# Chiến lược 4: Fallback quét text UTF-8
# ─────────────────────────────────────────────────────────────────────────────

def _parse_text_fallback(data: bytes) -> list[Question]:
    """Cố đọc file như UTF-8 text, tìm pattern câu hỏi."""
    try:
        text = data.decode("utf-8", errors="ignore")
    except Exception:
        return []

    # Tìm pattern "1. ... 2. ..." hoặc "Question 1"
    pattern = re.compile(
        r"(?:Question\s*\d+[:\.]?\s*|^\d+[\.\)]\s*)(.{20,500}?)(?=Question\s*\d+|\Z)",
        re.DOTALL | re.MULTILINE,
    )
    matches = pattern.findall(text)
    if len(matches) < 3:
        return []

    return [
        Question(
            id=str(i + 1),
            domain="General",
            text=m.strip()[:500],
            options=[],
            correct=[],
            explanation="",
        )
        for i, m in enumerate(matches)
    ]
