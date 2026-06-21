"""
Storage — lưu/đọc lịch sử làm bài dưới dạng JSON local.
"""

from __future__ import annotations

import json
import os
import logging
from datetime import date
from typing import TypedDict

logger = logging.getLogger(__name__)

HISTORY_FILE = "history.json"
MAX_HISTORY = 100   # giữ tối đa 100 bản ghi


class HistoryEntry(TypedDict):
    date: str          # ISO 8601: "2026-06-21"
    vce_file: str      # tên file .vce (không có đường dẫn đầy đủ)
    mode: str          # "exam" | "study"
    domain: str        # "Tất cả" hoặc tên domain
    correct: int
    total: int
    percent: float
    passed: bool
    elapsed_seconds: int


def _get_history_path() -> str:
    """Trả về đường dẫn file lịch sử (cùng thư mục app hoặc thư mục người dùng)."""
    # Trên Android: app_path là thư mục dữ liệu private
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and hasattr(app, "user_data_dir"):
            return os.path.join(app.user_data_dir, HISTORY_FILE)
    except ImportError:
        pass
    # Desktop fallback
    return HISTORY_FILE


def load_history() -> list[HistoryEntry]:
    """Đọc lịch sử từ file JSON. Trả về list rỗng nếu chưa có."""
    path = _get_history_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Không đọc được lịch sử: %s", e)
        return []


def save_history_entry(entry: HistoryEntry) -> None:
    """Thêm một bản ghi mới vào lịch sử."""
    history = load_history()
    history.insert(0, entry)       # mới nhất lên đầu
    history = history[:MAX_HISTORY]

    path = _get_history_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.error("Không lưu được lịch sử: %s", e)


def record_session(score: dict, vce_file: str, domain: str) -> None:
    """Tạo HistoryEntry từ kết quả get_score() và lưu."""
    entry: HistoryEntry = {
        "date": date.today().isoformat(),
        "vce_file": os.path.basename(vce_file),
        "mode": score.get("mode", "exam"),
        "domain": domain,
        "correct": score["correct"],
        "total": score["total"],
        "percent": score["percent"],
        "passed": score["passed"],
        "elapsed_seconds": score.get("elapsed_seconds", 0),
    }
    save_history_entry(entry)


def clear_history() -> None:
    """Xóa toàn bộ lịch sử làm bài."""
    path = _get_history_path()
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError as e:
        logger.warning("Không xóa được lịch sử: %s", e)
