"""
ECBA Exam Simulator — entry point Kivy app.

Chạy desktop: python main.py
Build APK:    xem hướng dẫn trong README.md (GitHub Actions)
"""

from __future__ import annotations

from kivy.config import Config

# Cài độ phân giải giả lập Android trước khi import kivy
Config.set("graphics", "width", "400")
Config.set("graphics", "height", "800")

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from src.vce_parser import Question
from src.exam_engine import ExamSession
from src.storage import record_session
from src.ui.home_screen import HomeScreen
from src.ui.exam_screen import ExamScreen
from src.ui.result_screen import ResultScreen


class ECBAExamApp(MDApp):
    title = "ECBA Exam Simulator"

    # State toàn cục
    _current_vce_file: str = ""
    _current_domain: str = "Tất cả"

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ExamScreen(name="exam"))
        sm.add_widget(ResultScreen(name="result"))
        return sm

    # ------------------------------------------------------------------ #
    # Navigation helpers (gọi từ các screen)

    def start_exam(
        self,
        questions: list[Question],
        mode: str,
        domain_filter: str | None,
        vce_file: str,
    ):
        self._current_vce_file = vce_file
        self._current_domain = domain_filter or "Tất cả"
        try:
            session = ExamSession.create(
                all_questions=questions,
                mode=mode,
                domain_filter=domain_filter,
                shuffle=True,
            )
        except ValueError as e:
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text=str(e)).open()
            return

        exam_screen: ExamScreen = self.root.get_screen("exam")
        exam_screen.start_session(session)
        self.root.current = "exam"

    def show_result(self, session: ExamSession):
        score = session.get_score()
        record_session(score, self._current_vce_file, self._current_domain)

        result_screen: ResultScreen = self.root.get_screen("result")
        result_screen.show_result(session)
        self.root.current = "result"

    def retry_exam(self, prev_session: ExamSession):
        """Thi lại với cùng câu hỏi (shuffle lại)."""
        home: HomeScreen = self.root.get_screen("home")
        self.start_exam(
            questions=prev_session.questions,
            mode=prev_session.mode,
            domain_filter=None,
            vce_file=self._current_vce_file,
        )


if __name__ == "__main__":
    ECBAExamApp().run()
