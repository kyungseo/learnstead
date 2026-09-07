import tempfile
import unittest
from datetime import date
from pathlib import Path

from ledger.parse import Record
from ledger.store import append_records, count_lines


class StoreTest(unittest.TestCase):
    def test_append_and_count(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.jsonl"
            recs = [Record(date(2026, 8, 1), "식비", -1000, "a")]
            self.assertEqual(append_records(p, recs), 1)
            self.assertEqual(append_records(p, recs), 1)
            self.assertEqual(count_lines(p), 2)
