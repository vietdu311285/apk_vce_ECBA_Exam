"""
Home Screen — màn hình chủ: chọn file .vce, cài đặt, xem lịch sử.
"""

from __future__ import annotations

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty

from src.vce_parser import parse_vce, get_domains, VCEParseError
from src.storage import load_history


class HomeScreen(Screen):
    selected_vce: str = ""
    questions = []
    domains: list[str] = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()
        self._file_manager = MDFileManager(
            exit_manager=self._close_file_manager,
            select_path=self._on_file_selected,
            ext=[".vce"],
        )
        self._domain_menu = None

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        # Tiêu đề
        root.add_widget(MDLabel(
            text="ECBA Exam Simulator",
            halign="center",
            font_style="H5",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(48),
        ))

        # Chọn file
        self.lbl_file = MDLabel(
            text="Chưa chọn file .vce",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(32),
        )
        root.add_widget(self.lbl_file)

        btn_pick = MDRaisedButton(
            text="Chọn file .vce",
            size_hint=(1, None),
            height=dp(48),
        )
        btn_pick.bind(on_release=self._open_file_manager)
        root.add_widget(btn_pick)

        # Domain filter
        domain_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        domain_row.add_widget(MDLabel(text="Domain:", size_hint_x=None, width=dp(80)))
        self.btn_domain = MDFlatButton(
            text="Tất cả",
            size_hint_x=1,
        )
        self.btn_domain.bind(on_release=self._open_domain_menu)
        domain_row.add_widget(self.btn_domain)
        root.add_widget(domain_row)

        # Mode toggle
        mode_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        mode_row.add_widget(MDLabel(text="Ôn tập (xem đáp án ngay):"))
        self.switch_study = MDSwitch()
        mode_row.add_widget(self.switch_study)
        root.add_widget(mode_row)

        # Nút bắt đầu
        self.btn_start = MDRaisedButton(
            text="Bắt đầu thi",
            size_hint=(1, None),
            height=dp(52),
            disabled=True,
        )
        self.btn_start.bind(on_release=self._start_exam)
        root.add_widget(self.btn_start)

        # Lịch sử
        root.add_widget(MDLabel(
            text="Lịch sử làm bài",
            font_style="H6",
            size_hint_y=None,
            height=dp(36),
        ))

        scroll = ScrollView()
        self.history_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(6),
        )
        self.history_box.bind(minimum_height=self.history_box.setter("height"))
        scroll.add_widget(self.history_box)
        root.add_widget(scroll)

        self.add_widget(root)

    def on_enter(self):
        """Gọi mỗi khi màn hình được hiển thị — làm mới lịch sử."""
        self._refresh_history()

    def _open_file_manager(self, *_):
        import os
        start_path = "/"
        try:
            from android.storage import primary_external_storage_path  # type: ignore
            start_path = primary_external_storage_path()
        except ImportError:
            start_path = os.path.expanduser("~")
        self._file_manager.show(start_path)

    def _close_file_manager(self, *_):
        self._file_manager.close()

    def _on_file_selected(self, path: str):
        self._file_manager.close()
        self.lbl_file.text = f"Đang đọc: {path.split('/')[-1]}..."
        Clock.schedule_once(lambda dt: self._load_vce(path), 0.1)

    def _load_vce(self, path: str):
        try:
            self.questions = parse_vce(path)
            self.selected_vce = path
            self.domains = get_domains(self.questions)
            self.btn_domain.text = "Tất cả"
            self.lbl_file.text = f"{path.split('/')[-1]}  ({len(self.questions)} câu)"
            self.btn_start.disabled = False
            self._build_domain_menu()
        except (VCEParseError, FileNotFoundError) as e:
            self.lbl_file.text = f"Lỗi: {e}"
            self.btn_start.disabled = True

    def _build_domain_menu(self):
        items = [
            {"text": d, "viewclass": "OneLineListItem",
             "on_release": lambda x=d: self._set_domain(x)}
            for d in self.domains
        ]
        self._domain_menu = MDDropdownMenu(
            caller=self.btn_domain,
            items=items,
            width_mult=4,
        )

    def _open_domain_menu(self, *_):
        if self._domain_menu:
            self._domain_menu.open()

    def _set_domain(self, domain: str):
        self.btn_domain.text = domain
        if self._domain_menu:
            self._domain_menu.dismiss()

    def _start_exam(self, *_):
        if not self.questions:
            return
        app = self.manager.parent
        domain = self.btn_domain.text
        mode = "study" if self.switch_study.active else "exam"

        app.start_exam(
            questions=self.questions,
            mode=mode,
            domain_filter=domain if domain != "Tất cả" else None,
            vce_file=self.selected_vce,
        )

    def _refresh_history(self):
        self.history_box.clear_widgets()
        history = load_history()[:5]  # hiển thị 5 lần gần nhất

        if not history:
            self.history_box.add_widget(MDLabel(
                text="Chưa có lần thi nào.",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(32),
            ))
            return

        for entry in history:
            result_icon = "✓" if entry["passed"] else "✗"
            result_color = "Primary" if entry["passed"] else "Error"
            card = MDCard(
                size_hint_y=None,
                height=dp(64),
                padding=dp(8),
            )
            row = BoxLayout()
            row.add_widget(MDLabel(
                text=f"{entry['date']}  {entry['vce_file']}",
                theme_text_color="Secondary",
                font_style="Caption",
            ))
            row.add_widget(MDLabel(
                text=f"{result_icon} {entry['correct']}/{entry['total']} ({entry['percent']}%)",
                halign="right",
                theme_text_color=result_color,
            ))
            card.add_widget(row)
            self.history_box.add_widget(card)
