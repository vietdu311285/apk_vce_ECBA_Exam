"""
Unit tests cho vce_parser.py — chạy: python -m pytest tests/ -v
"""

import io
import os
import sys
import zipfile
import xml.etree.ElementTree as ET
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.vce_parser import parse_vce, get_domains, VCEParseError, Question


def _make_vce_zip(questions_xml: str, filename: str = "exam.xml") -> bytes:
    """Tạo file .vce giả (ZIP/XML) trong memory để test."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(filename, questions_xml)
    return buf.getvalue()


SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Exam title="ECBA Sample">
  <Question id="1">
    <Domain>Business Analysis Planning</Domain>
    <QuestionText>What is the primary output of the planning process?</QuestionText>
    <Answer correct="false">A work breakdown structure</Answer>
    <Answer correct="true">A business analysis plan</Answer>
    <Answer correct="false">A project charter</Answer>
    <Answer correct="false">A stakeholder register</Answer>
    <Explanation>The business analysis plan guides all BA activities.</Explanation>
  </Question>
  <Question id="2">
    <Domain>Elicitation</Domain>
    <QuestionText>Which technique is best for gathering tacit knowledge?</QuestionText>
    <Answer correct="false">Survey</Answer>
    <Answer correct="true">Interview</Answer>
    <Answer correct="false">Document analysis</Answer>
    <Answer correct="false">Observation</Answer>
    <Explanation>Interviews allow probing for unstated knowledge.</Explanation>
  </Question>
  <Question id="3">
    <Domain>Elicitation</Domain>
    <QuestionText>Select all valid elicitation techniques. (Multi-select)</QuestionText>
    <Answer correct="true">Workshop</Answer>
    <Answer correct="true">Focus group</Answer>
    <Answer correct="false">Risk register</Answer>
    <Answer correct="false">Gantt chart</Answer>
  </Question>
</Exam>"""


class TestVCEParser(unittest.TestCase):

    def setUp(self):
        """Ghi file .vce tạm ra đĩa để test."""
        self.tmp_path = "tests/_tmp_test.vce"
        vce_bytes = _make_vce_zip(SAMPLE_XML)
        with open(self.tmp_path, "wb") as f:
            f.write(vce_bytes)

    def tearDown(self):
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    def test_parse_returns_list(self):
        questions = parse_vce(self.tmp_path)
        self.assertIsInstance(questions, list)

    def test_question_count(self):
        questions = parse_vce(self.tmp_path)
        self.assertEqual(len(questions), 3)

    def test_question_fields(self):
        q = parse_vce(self.tmp_path)[0]
        self.assertIsInstance(q, Question)
        self.assertTrue(q.text)
        self.assertTrue(q.options)
        self.assertIsInstance(q.correct, list)
        self.assertGreater(len(q.options), 0)

    def test_correct_answer_index(self):
        questions = parse_vce(self.tmp_path)
        q0 = questions[0]
        # Đáp án đúng là "A business analysis plan" — index 1
        self.assertIn(1, q0.correct)
        self.assertEqual(len(q0.correct), 1)

    def test_multi_correct(self):
        questions = parse_vce(self.tmp_path)
        q2 = questions[2]
        self.assertEqual(q2.question_type, "multi")
        self.assertEqual(sorted(q2.correct), [0, 1])

    def test_domain_extracted(self):
        questions = parse_vce(self.tmp_path)
        self.assertEqual(questions[0].domain, "Business Analysis Planning")
        self.assertEqual(questions[1].domain, "Elicitation")

    def test_explanation_extracted(self):
        questions = parse_vce(self.tmp_path)
        self.assertIn("business analysis plan", questions[0].explanation.lower())

    def test_get_domains(self):
        questions = parse_vce(self.tmp_path)
        domains = get_domains(questions)
        self.assertEqual(domains[0], "Tất cả")
        self.assertIn("Elicitation", domains)
        self.assertIn("Business Analysis Planning", domains)

    def test_bad_zip_raises(self):
        bad_path = "tests/_bad.vce"
        with open(bad_path, "wb") as f:
            f.write(b"not a zip file")
        try:
            with self.assertRaises(VCEParseError):
                parse_vce(bad_path)
        finally:
            os.remove(bad_path)

    def test_file_not_found_raises(self):
        with self.assertRaises(FileNotFoundError):
            parse_vce("nonexistent_file.vce")

    def test_real_vce_file(self):
        """Test với file .vce thực nếu có trong thư mục tests/."""
        real_vce = "tests/sample.vce"
        if not os.path.exists(real_vce):
            self.skipTest("Không có file sample.vce thực để test")
        questions = parse_vce(real_vce)
        self.assertGreater(len(questions), 0, "File .vce thực không parse được câu hỏi nào")
        print(f"\n[REAL VCE] {len(questions)} câu, domains: {get_domains(questions)}")
        print(f"  Câu 1: {questions[0].text[:80]}...")


if __name__ == "__main__":
    unittest.main(verbosity=2)
