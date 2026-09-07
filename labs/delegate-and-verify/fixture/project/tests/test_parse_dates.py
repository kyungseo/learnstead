import unittest
from datetime import date

from ledger.parse import parse_date


class ParseDateTest(unittest.TestCase):
    def test_parse_date(self):
        self.assertEqual(parse_date("2026-08-31"), date(2026, 8, 31))
