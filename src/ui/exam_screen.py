"""
Exam Screen — màn hình thi: câu hỏi, đáp án, timer.
"""

from __future__ import annotations

import io
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image as KivyImage
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog

from src.exam_engine import ExamSession
from src.vce_parser import Question


class ExamScreen(Screen):
    session: ExamSession | None = None
    _timer_event = None
    _selected: list[int] = []
    _answer_submitted: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        # Header: timer + progress
        header = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.lbl_progress = MDLabel(
            text="Câu 1/50",
            font_style="Subtitle1",
            size_hint_x=0.6,
        )
        self.lbl_timer = MDLabel(
            text="02:30:00",
            halign="right",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_x=0.4,
        )
        header.add_widget(self.lbl_progress)
        header.add_widget(self.lbl_timer)
        root.add_widget(header)

        # Câu hỏi
        scroll = ScrollView(size_hint_y=0.45)
        q_box = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(4))
        q_box.bind(minimum_height=q_box.setter("height"))

        self.lbl_question = MDLabel(
            text="",
            size_hint_y=None,
            text_size=(None, None),
            halign="left",
        )
        self.lbl_question.bind(
            texture_size=lambda inst, val: setattr(inst, "height", val[1] + dp(8))
        )
        q_box.add_widget(self.lbl_question)

        self.img_question = KivyImage(
            size_hint_y=None,
            height=0,
            allow_stretch=True,
        )
        q_box.add_widget(self.img_question)
        scroll.add_widget(q_box)
        root.add_widget(scroll)

        # Khu vực đáp án
        ans_scroll = ScrollView(size_hint_y=0.35)
        self.ans_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(6),
            padding=dp(4),
        )
        self.ans_box.bind(minimum_height=self.ans_box.setter("height"))
        ans_scroll.add_widget(self.ans_box)
        root.add_widget(ans_scroll)

        # Giải thích (mode study)
        self.lbl_explanation = MDLabel(
            text="",
            size_hint_y=None,
            height=0,
            theme_text_color="Secondary",
            italic=True,
        )
        self.lbl_explanation.bind(
            texture_size=lambda inst, val: setattr(inst, "height", val[1] + dp(4))
        )
        root.add_widget(self.lbl_explanation)

        # Footer buttons
        footer = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        self.btn_submit = MDRaisedButton(
            text="Xác nhận",
            size_hint_x=0.5,
            disabled=True,
        )
        self.btn_submit.bind(on_release=self._submit_answer)

        self.btn_next = MDRaisedButton(
            text="Tiếp →",
            size_hint_x=0.5,
            disabled=True,
        )
        self.btn_next.bind(on_release=self._go_next)

        btn_quit = MDFlatButton(text="Thoát", size_hint_x=None, width=dp(72))
        btn_quit.bind(on_release=self._confirm_quit)

        footer.add_widget(btn_quit)
        footer.add_widget(self.btn_submit)
        footer.add_widget(self.btn_next)
        root.add_widget(footer)

        self.add_widget(root)

    # ------------------------------------------------------------------ #
    # Public API

    def start_session(self, session: ExamSession):
        self.session = session
        self._selected = []
        self._answer_submitted = False

        if self._timer_event:
            self._timer_event.cancel()

        if session.mode == "exam":
            self.lbl_timer.opacity = 1
            self._timer_event = Clock.schedule_interval(self._update_timer, 1)
        else:
            self.lbl_timer.opacity = 0

        self._render_question()

    # ------------------------------------------------------------------ #
    # UI helpers

    def _render_question(self):
        if not self.session:
            return
        q = self.session.current_question
        if q is None:
            self._finish_exam()
            return

        idx = self.session.current_index
        total = self.session.total
        self.lbl_progress.text = f"Câu {idx + 1}/{total}"
        self.lbl_question.text = q.text
        self.lbl_explanation.text = ""
        self.lbl_explanation.height = 0

        # Ảnh câu hỏi
        if q.image_data:
            buf = io.BytesIO(q.image_data)
            core_img = CoreImage(buf, ext="png")
            self.img_question.texture = core_img.texture
            self.img_question.height = dp(180)
        else:
            self.img_question.texture = None
            self.img_question.height = 0

        self._build_answer_widgets(q)
        self._selected = []
        self._answer_submitted = False
        self.btn_submit.disabled = True
        self.btn_next.disabled = True

    def _build_answer_widgets(self, q: Question):
        self.ans_box.clear_widgets()
        is_multi = q.question_type == "multi"

        for i, opt in enumerate(q.options):
            row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
            cb = MDCheckbox(
                group="" if is_multi else "answers",
                size_hint=(None, None),
                size=(dp(32), dp(32)),
            )
            cb.option_index = i
            cb.bind(active=self._on_answer_toggle)

            label = MDLabel(text=f"{chr(65 + i)}. {opt}")
            row.add_widget(cb)
            row.add_widget(label)

            card = MDCard(size_hint_y=None, height=dp(48), padding=dp(4))
            card.add_widget(row)
            self.ans_box.add_widget(card)

    def _on_answer_toggle(self, checkbox, active):
        idx = checkbox.option_index
        if active:
            if idx not in self._selected:
                self._selected.append(idx)
        else:
            if idx in self._selected:
                self._selected.remove(idx)
        self.btn_submit.disabled = not self._selected

    def _submit_answer(self, *_):
        if not self.session or self._answer_submitted:
            return
        record = self.session.submit_answer(self._selected)
        self._answer_submitted = True
        self.btn_submit.disabled = True
        self.btn_next.disabled = False

        q = self.session.current_question
        # Highlight đáp án đúng/sai
        self._highlight_answers(q, record.is_correct)

        # Mode study: hiện giải thích ngay
        if self.session.mode == "study" and q and q.explanation:
            self.lbl_explanation.text = f"Giải thích: {q.explanation}"

    def _highlight_answers(self, q, is_correct: bool):
        """Tô màu đúng/sai trên các card đáp án."""
        for i, card in enumerate(self.ans_box.children[::-1]):
            if i in (q.correct if q else []):
                card.md_bg_color = [0.2, 0.7, 0.2, 0.3]   # xanh = đúng
            elif i in self._selected and i not in (q.correct if q else []):
                card.md_bg_color = [0.9, 0.2, 0.2, 0.3]   # đỏ = sai

    def _go_next(self, *_):
        if not self.session:
            return
        has_more = self.session.next_question()
        if has_more:
            self._render_question()
        else:
            self._finish_exam()

    def _update_timer(self, dt):
        if not self.session:
            return
        remaining = int(self.session.remaining_seconds)
        h, m, s = remaining // 3600, (remaining % 3600) // 60, remaining % 60
        self.lbl_timer.text = f"{h:02d}:{m:02d}:{s:02d}"

        if self.session.is_time_up:
            self._finish_exam()

    def _finish_exam(self):
        if self._timer_event:
            self._timer_event.cancel()
        app = self.manager.parent
        app.show_result(self.session)

    def _confirm_quit(self, *_):
        dialog = MDDialog(
            title="Thoát bài thi?",
            text="Kết quả sẽ không được lưu nếu chưa hoàn thành.",
            buttons=[
                MDFlatButton(
                    text="Ở lại",
                    on_release=lambda *a: dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="Thoát",
                    on_release=lambda *a: self._do_quit(dialog),
                ),
            ],
        )
        dialog.open()

    def _do_quit(self, dialog):
        dialog.dismiss()
        if self._timer_event:
            self._timer_event.cancel()
        self.manager.current = "home"
