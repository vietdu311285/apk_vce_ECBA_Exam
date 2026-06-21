"""
Exam engine — quản lý phiên thi: shuffle, timer, chấm điểm, lọc domain.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Literal

from src.vce_parser import Question

# ECBA: 50 câu / 150 phút
ECBA_TIMER_SECONDS = 150 * 60
ECBA_PASS_PERCENT = 70.0


@dataclass
class AnswerRecord:
    question_id: str
    chosen: list[int]      # index đáp án người dùng chọn
    correct: list[int]     # index đáp án đúng
    is_correct: bool
    time_spent: float      # giây dành cho câu này


@dataclass
class ExamSession:
    questions: list[Question]
    mode: Literal["exam", "study"]   # exam = timer | study = xem đáp án ngay
    timer_seconds: int = ECBA_TIMER_SECONDS

    # Runtime state
    current_index: int = 0
    answers: list[AnswerRecord] = field(default_factory=list)
    _start_time: float = field(default_factory=time.time, init=False)
    _q_start_time: float = field(default_factory=time.time, init=False)
    finished: bool = False

    @classmethod
    def create(
        cls,
        all_questions: list[Question],
        mode: Literal["exam", "study"],
        domain_filter: str | None = None,
        shuffle: bool = True,
        timer_seconds: int = ECBA_TIMER_SECONDS,
    ) -> "ExamSession":
        """Tạo phiên thi mới với filter và shuffle tùy chọn."""
        questions = list(all_questions)

        if domain_filter and domain_filter != "Tất cả":
            questions = [q for q in questions if q.domain == domain_filter]

        if not questions:
            raise ValueError(
                f"Không có câu hỏi nào"
                + (f" trong domain '{domain_filter}'" if domain_filter else "")
            )

        if shuffle:
            random.shuffle(questions)
            for q in questions:
                if shuffle:
                    shuffled_options = list(enumerate(q.options))
                    random.shuffle(shuffled_options)
                    old_to_new = {old: new for new, (old, _) in enumerate(shuffled_options)}
                    object.__setattr__(q, "options", [opt for _, opt in shuffled_options])
                    object.__setattr__(
                        q, "correct", [old_to_new[c] for c in q.correct]
                    )

        return cls(questions=questions, mode=mode, timer_seconds=timer_seconds)

    @property
    def current_question(self) -> Question | None:
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    @property
    def total(self) -> int:
        return len(self.questions)

    @property
    def elapsed_seconds(self) -> float:
        return time.time() - self._start_time

    @property
    def remaining_seconds(self) -> float:
        return max(0.0, self.timer_seconds - self.elapsed_seconds)

    @property
    def is_time_up(self) -> bool:
        return self.mode == "exam" and self.remaining_seconds <= 0

    def submit_answer(self, chosen: list[int]) -> AnswerRecord:
        """Ghi nhận đáp án cho câu hiện tại, trả về AnswerRecord."""
        q = self.current_question
        if q is None:
            raise RuntimeError("Không có câu hỏi hiện tại để nộp đáp án.")

        is_correct = sorted(chosen) == sorted(q.correct)
        time_spent = time.time() - self._q_start_time

        record = AnswerRecord(
            question_id=q.id,
            chosen=chosen,
            correct=q.correct,
            is_correct=is_correct,
            time_spent=time_spent,
        )
        self.answers.append(record)
        return record

    def next_question(self) -> bool:
        """Chuyển sang câu tiếp theo. Trả về False nếu đã hết."""
        self.current_index += 1
        self._q_start_time = time.time()
        if self.current_index >= self.total:
            self.finished = True
            return False
        return True

    def skip_question(self) -> None:
        """Bỏ qua câu hiện tại (không ghi nhận đáp án)."""
        self.answers.append(AnswerRecord(
            question_id=self.current_question.id if self.current_question else "",
            chosen=[],
            correct=self.current_question.correct if self.current_question else [],
            is_correct=False,
            time_spent=time.time() - self._q_start_time,
        ))
        self.next_question()

    def get_score(self) -> dict:
        """Tính kết quả phiên thi."""
        answered = [r for r in self.answers if r.chosen]
        correct_count = sum(1 for r in answered if r.is_correct)
        total = self.total
        percent = (correct_count / total * 100) if total > 0 else 0.0

        return {
            "correct": correct_count,
            "total": total,
            "answered": len(answered),
            "skipped": total - len(self.answers),
            "percent": round(percent, 1),
            "passed": percent >= ECBA_PASS_PERCENT,
            "elapsed_seconds": int(self.elapsed_seconds),
            "mode": self.mode,
        }

    def get_wrong_answers(self) -> list[tuple[Question, AnswerRecord]]:
        """Trả về danh sách (câu hỏi, record) của những câu sai."""
        wrong = []
        q_map = {q.id: q for q in self.questions}
        for record in self.answers:
            if not record.is_correct:
                q = q_map.get(record.question_id)
                if q:
                    wrong.append((q, record))
        return wrong
