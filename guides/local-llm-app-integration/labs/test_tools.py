#!/usr/bin/env python3
"""모델 호출 없이 tool 경계를 확인하는 회귀 테스트."""

import unittest

import agent_readonly as agent


class ToolBoundaryTest(unittest.TestCase):
    def test_calculator_accepts_bounded_arithmetic(self):
        self.assertEqual(agent.calculate("(15 + 5) * 2"), "40")

    def test_calculator_rejects_code_execution(self):
        self.assertIn("오류:", agent.calculate("__import__('os').listdir('.')"))

    def test_calculator_rejects_resource_exhaustion(self):
        self.assertIn("오류:", agent.calculate("9 ** 999999"))

    def test_path_boundary_rejects_parent(self):
        self.assertIn("허용되지 않은 경로", agent.read_doc("../secret/비밀-메모.md"))

    def test_demo_switch_allows_only_fixture_secret(self):
        fixture = agent.read_doc("../secret/비밀-메모.md", allow_fixture_secret=True)
        self.assertIn("실습용 가짜 데이터", fixture)
        self.assertIn("허용되지 않은 경로", agent.read_doc("../../README.md", allow_fixture_secret=True))

    def test_only_markdown_files_are_allowed(self):
        self.assertIn("Markdown 문서만", agent.read_doc("공지.txt"))

    def test_empty_search_is_rejected(self):
        self.assertIn("검색어가 비어", agent.search_docs(""))


if __name__ == "__main__":
    unittest.main()
