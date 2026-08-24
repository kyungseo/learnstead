#!/usr/bin/env python3
"""Learnstead validator의 공개 경계 회귀 테스트."""

import unittest

import validate


class MachineLocalPathTest(unittest.TestCase):
    def violations(self, text: str) -> list[str]:
        return [
            match.group(1)
            for match in validate.MACHINE_LOCAL_PATH.finditer(text)
            if match.group(1) not in validate.APPROVED_PATH_PLACEHOLDERS
        ]

    def test_approved_placeholders(self):
        for path in (
            "/Users/내이름/project",
            "/Users/사용자이름/project",
            "/Users/USERNAME/project",
            "/Users/<username>/project",
            "/Users/{username}/project",
            "/c/Users/내이름/Documents/내-프로젝트",
        ):
            with self.subTest(path=path):
                self.assertEqual([], self.violations(path))

    def test_actual_user_segment_is_rejected(self):
        path = "/" + "Users" + "/alice/private-project"
        self.assertEqual(["alice"], self.violations(f"cd {path}"))


if __name__ == "__main__":
    unittest.main()
