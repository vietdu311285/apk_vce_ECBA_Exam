"""ECBA Exam Simulator - Simplified version (Kivy only, no KivyMD)"""

import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.metrics import dp

from src.vce_parser import parse_vce, get_domains
from src.exam_engine import ExamSession
from src.storage import load_history, record_session


class ECBAApp(App):
    title = "ECBA Exam"
    questions = []
    session = None
    domains = []

    def build(self):
        self.root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self._build_home_screen()
        return self.root

    def _build_home_screen(self):
        """Main screen - file selection & exam settings"""
        self.root.clear_widgets()

        # Title
        self.root.add_widget(Label(text="ECBA Exam Simulator", size_hint_y=0.1, font_size='20sp'))

        # File chooser
        self.root.add_widget(Label(text="Select VCE file:", size_hint_y=0.05))
        filechooser = FileChooserListView(filters=['*.vce'], size_hint_y=0.3)
        filechooser.bind(selection=self._on_file_select)
        self.root.add_widget(filechooser)

        self.file_label = Label(text="No file selected", size_hint_y=0.05)
        self.root.add_widget(self.file_label)

        # Mode selector
        mode_row = BoxLayout(size_hint_y=0.08, spacing=dp(5))
        mode_row.add_widget(Label(text="Mode:", size_hint_x=0.2))
        self.mode_btn = ToggleButton(text='Exam (timed)', state='down', size_hint_x=0.4)
        self.study_btn = ToggleButton(text='Study', size_hint_x=0.4, group='mode')
        self.mode_btn.group = 'mode'
        mode_row.add_widget(self.mode_btn)
        mode_row.add_widget(self.study_btn)
        self.root.add_widget(mode_row)

        # Domain filter
        domain_row = BoxLayout(size_hint_y=0.08, spacing=dp(5))
        domain_row.add_widget(Label(text="Domain:", size_hint_x=0.2))
        self.domain_spinner = Spinner(text='Tất cả', values=self.domains or ['Tất cả'], size_hint_x=0.8)
        domain_row.add_widget(self.domain_spinner)
        self.root.add_widget(domain_row)

        # History
        self.root.add_widget(Label(text="Recent:", size_hint_y=0.05))
        history = load_history()[:3]
        hist_text = "\n".join([f"{h['date']}: {h['correct']}/{h['total']} ({h['percent']}%)"
                               for h in history]) if history else "No history"
        self.root.add_widget(Label(text=hist_text, size_hint_y=0.15))

        # Start button
        btn_start = Button(text='Start Exam', size_hint_y=0.08, background_color=(0.2, 0.6, 0.2, 1))
        btn_start.bind(on_press=self._start_exam)
        self.root.add_widget(btn_start)

    def _on_file_select(self, instance, selection):
        if selection:
            file_path = selection[0]
            try:
                self.questions = parse_vce(file_path)
                self.domains = get_domains(self.questions)
                self.domain_spinner.values = self.domains
                self.file_label.text = f"{os.path.basename(file_path)} - {len(self.questions)} questions"
            except Exception as e:
                self.file_label.text = f"Error: {str(e)[:50]}"

    def _start_exam(self, instance):
        if not self.questions:
            self.file_label.text = "Please select a VCE file first"
            return

        mode = 'exam' if self.mode_btn.state == 'down' else 'study'
        domain = self.domain_spinner.text if self.domain_spinner.text != 'Tất cả' else None

        try:
            self.session = ExamSession.create(
                all_questions=self.questions,
                mode=mode,
                domain_filter=domain,
                shuffle=True
            )
            self._show_exam_screen()
        except Exception as e:
            self.file_label.text = f"Error: {str(e)[:50]}"

    def _show_exam_screen(self):
        """Exam screen - show question & answers"""
        self.root.clear_widgets()

        # Header
        header = BoxLayout(size_hint_y=0.08, spacing=dp(10))
        self.progress_label = Label(text="Question 1/50")
        self.timer_label = Label(text="2:30:00")
        header.add_widget(self.progress_label)
        header.add_widget(self.timer_label)
        self.root.add_widget(header)

        # Question
        scroll_q = ScrollView(size_hint_y=0.25)
        self.question_label = Label(text="", size_hint_y=None, markup=True)
        self.question_label.bind(texture_size=self.question_label.setter('size'))
        scroll_q.add_widget(self.question_label)
        self.root.add_widget(scroll_q)

        # Answers
        scroll_a = ScrollView(size_hint_y=0.35)
        self.answers_box = GridLayout(cols=1, size_hint_y=None, spacing=dp(5))
        self.answers_box.bind(minimum_height=self.answers_box.setter('height'))
        scroll_a.add_widget(self.answers_box)
        self.root.add_widget(scroll_a)

        # Explanation (study mode)
        self.explanation_label = Label(text="", size_hint_y=0.1, markup=True)
        self.root.add_widget(self.explanation_label)

        # Buttons
        btn_row = BoxLayout(size_hint_y=0.08, spacing=dp(5))
        btn_submit = Button(text='Submit', size_hint_x=0.33)
        btn_submit.bind(on_press=self._submit_answer)
        btn_next = Button(text='Next', size_hint_x=0.33)
        btn_next.bind(on_press=self._next_question)
        btn_quit = Button(text='Quit', size_hint_x=0.34, background_color=(0.8, 0.2, 0.2, 1))
        btn_quit.bind(on_press=self._quit_exam)
        btn_row.add_widget(btn_submit)
        btn_row.add_widget(btn_next)
        btn_row.add_widget(btn_quit)
        self.root.add_widget(btn_row)

        # Timer
        if self.session.mode == 'exam':
            self._timer_event = Clock.schedule_interval(self._update_timer, 1)

        self._render_question()

    def _render_question(self):
        """Display current question"""
        q = self.session.current_question
        if q is None:
            self._finish_exam()
            return

        idx = self.session.current_index
        self.progress_label.text = f"Question {idx + 1}/{self.session.total}"
        self.question_label.text = q.text
        self.explanation_label.text = ""

        self.answers_box.clear_widgets()
        self.selected_answer = None

        for i, opt in enumerate(q.options):
            btn = ToggleButton(text=f"{chr(65 + i)}. {opt}", size_hint_y=None, height=dp(40), group='answers')
            btn.option_idx = i
            btn.bind(state=self._on_answer_select)
            self.answers_box.add_widget(btn)

    def _on_answer_select(self, instance, value):
        if value == 'down':
            self.selected_answer = instance.option_idx

    def _submit_answer(self, instance):
        if self.selected_answer is None:
            return
        q = self.session.current_question
        self.session.submit_answer([self.selected_answer])

        if self.session.mode == 'study' and q and q.explanation:
            self.explanation_label.text = f"[b]Answer:[/b] {chr(65 + self.selected_answer)}\n[b]Explanation:[/b] {q.explanation}"

    def _next_question(self, instance):
        has_more = self.session.next_question()
        if has_more:
            self._render_question()
        else:
            self._finish_exam()

    def _update_timer(self, dt):
        remaining = int(self.session.remaining_seconds)
        h, m, s = remaining // 3600, (remaining % 3600) // 60, remaining % 60
        self.timer_label.text = f"{h:02d}:{m:02d}:{s:02d}"
        if self.session.is_time_up:
            self._finish_exam()

    def _finish_exam(self):
        if hasattr(self, '_timer_event') and self._timer_event:
            self._timer_event.cancel()

        score = self.session.get_score()
        record_session(score, "exam.vce", "all")

        self.root.clear_widgets()
        result_box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        result_box.add_widget(Label(text=f"Results", size_hint_y=0.1, font_size='20sp'))
        result_box.add_widget(Label(
            text=f"{score['correct']}/{score['total']} ({score['percent']}%)\n"
                 f"{'PASS ✓' if score['passed'] else 'FAIL ✗'}",
            size_hint_y=0.3, font_size='18sp'
        ))

        btn_home = Button(text='Back to Home', size_hint_y=0.1)
        btn_home.bind(on_press=lambda x: self._build_home_screen())
        result_box.add_widget(btn_home)

        self.root.add_widget(result_box)

    def _quit_exam(self, instance):
        self._build_home_screen()


if __name__ == '__main__':
    ECBAApp().run()
