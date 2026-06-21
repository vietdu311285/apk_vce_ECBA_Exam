"""
Result Screen — màn hình kết quả sau khi thi xong.
"""

from __future__ import annotations

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard

from src.exam_engine import ExamSession, ECBA_PASS_PERCENT


class ResultScreen(Screen):
    session: ExamSession | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        # Điểm số chính
        self.lbl_score = MDLabel(
            text="",
            halign="center",
            font_style="H4",
            size_hint_y=None,
            height=dp(64),
        )
        root.add_widget(self.lbl_score)

        self.lbl_pass = MDLabel(
            text="",
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height=dp(48),
        )
        root.add_widget(self.lbl_pass)

        # Chi tiết
        self.lbl_detail = MDLabel(
            text="",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(40),
        )
        root.add_widget(self.lbl_detail)

        # Điểm theo domain
        root.add_widget(MDLabel(
            text="Kết quả theo domain",
            font_style="H6",
            size_hint_y=None,
            height=dp(36),
        ))
        domain_scroll = ScrollView(size_hint_y=0.3)
        self.domain_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(4),
        )
        self.domain_box.bind(minimum_height=self.domain_box.setter("height"))
        domain_scroll.add_widget(self.domain_box)
        root.add_widget(domain_scroll)

        # Review câu sai
        self.btn_review = MDFlatButton(
            text="Xem lại câu sai",
            size_hint=(1, None),
            height=dp(44),
        )
        self.btn_review.bind(on_release=self._toggle_review)
        root.add_widget(self.btn_review)

        review_scroll = ScrollView(size_hint_y=0)
        self.review_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8),
        )
        self.review_box.bind(minimum_height=self.review_box.setter("height"))
        review_scroll.add_widget(self.review_box)
        self.review_scroll = review_scroll
        root.add_widget(review_scroll)

        # Buttons
        btn_row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        btn_home = MDRaisedButton(
            text="Về trang chủ",
            size_hint_x=0.5,
        )
        btn_home.bind(on_release=self._go_home)

        btn_retry = MDFlatButton(
            text="Thi lại",
            size_hint_x=0.5,
        )
        btn_retry.bind(on_release=self._retry)

        btn_row.add_widget(btn_home)
        btn_row.add_widget(btn_retry)
        root.add_widget(btn_row)

        self.add_widget(root)
        self._review_open = False

    def show_result(self, session: ExamSession):
        self.session = session
        score = session.get_score()

        percent = score["percent"]
        passed = score["passed"]

        self.lbl_score.text = f"{score['correct']}/{score['total']}  ({percent}%)"
        if passed:
            self.lbl_pass.text = "✓  ĐẠT"
            self.lbl_pass.theme_text_color = "Custom"
            self.lbl_pass.text_color = [0.1, 0.7, 0.1, 1]
        else:
            self.lbl_pass.text = "✗  CHƯA ĐẠT"
            self.lbl_pass.theme_text_color = "Custom"
            self.lbl_pass.text_color = [0.8, 0.1, 0.1, 1]

        elapsed = score["elapsed_seconds"]
        h, m = elapsed // 3600, (elapsed % 3600) // 60
        self.lbl_detail.text = (
            f"Bỏ qua: {score['skipped']} câu  |  "
            f"Thời gian: {h:02d}h{m:02d}m  |  "
            f"Điểm đạt: ≥{int(ECBA_PASS_PERCENT)}%"
        )

        self._render_domain_stats(session)
        self._render_review(session)
        self._review_open = False
        self.review_scroll.size_hint_y = 0

    def _render_domain_stats(self, session: ExamSession):
        self.domain_box.clear_widgets()
        # Tính điểm từng domain
        domain_scores: dict[str, list[bool]] = {}
        q_map = {q.id: q for q in session.questions}
        for record in session.answers:
            q = q_map.get(record.question_id)
            domain = q.domain if q else "General"
            domain_scores.setdefault(domain, []).append(record.is_correct)

        for domain, results in sorted(domain_scores.items()):
            correct = sum(results)
            total = len(results)
            pct = round(correct / total * 100, 1) if total else 0
            icon = "✓" if pct >= ECBA_PASS_PERCENT else "✗"
            card = MDCard(size_hint_y=None, height=dp(44), padding=dp(8))
            row = BoxLayout()
            row.add_widget(MDLabel(text=domain, font_style="Caption"))
            row.add_widget(MDLabel(
                text=f"{icon} {correct}/{total} ({pct}%)",
                halign="right",
                font_style="Caption",
                theme_text_color="Primary" if pct >= ECBA_PASS_PERCENT else "Error",
            ))
            card.add_widget(row)
            self.domain_box.add_widget(card)

    def _render_review(self, session: ExamSession):
        self.review_box.clear_widgets()
        wrong = session.get_wrong_answers()

        if not wrong:
            self.btn_review.text = "Không có câu sai "
            self.btn_review.disabled = True
            return

        self.btn_review.text = f"Xem lại {len(wrong)} câu sai ▼"
        for q, record in wrong:
            card = MDCard(
                size_hint_y=None,
                padding=dp(10),
                radius=[dp(8)],
            )
            col = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
            col.bind(minimum_height=col.setter("height"))
            card.bind(minimum_height=card.setter("height"))

            col.add_widget(MDLabel(
                text=q.text,
                size_hint_y=None,
                text_size=(None, None),
                halign="left",
            ))

            chosen_letters = ", ".join(chr(65 + i) for i in record.chosen)
            correct_letters = ", ".join(chr(65 + i) for i in q.correct)
            col.add_widget(MDLabel(
                text=f"Bạn chọn: {chosen_letters}  |  Đúng: {correct_letters}",
                theme_text_color="Error",
                font_style="Caption",
                size_hint_y=None,
                height=dp(24),
            ))

            if q.explanation:
                col.add_widget(MDLabel(
                    text=f"Giải thích: {q.explanation}",
                    theme_text_color="Secondary",
                    italic=True,
                    font_style="Caption",
                    size_hint_y=None,
                    text_size=(None, None),
                ))

            card.add_widget(col)
            self.review_box.add_widget(card)

    def _toggle_review(self, *_):
        if self._review_open:
            self.review_scroll.size_hint_y = 0
            self._review_open = False
        else:
            self.review_scroll.size_hint_y = 0.4
            self._review_open = True

    def _go_home(self, *_):
        self.manager.current = "home"

    def _retry(self, *_):
        app = self.manager.parent
        if self.session:
            app.retry_exam(self.session)
