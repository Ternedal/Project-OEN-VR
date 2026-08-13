#!/usr/bin/env python3
"""Code QA for evaluate_mpre.py. Synthetic rows exist only in temporary files."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from evaluate_mpre import evaluate

HEADER = "session_id,pair_id,day1_seconds,day2_seconds,day3_seconds,disagreement_days,administration_observed,changed_mind_count,regret_after_storm,human_session,gift_recipient_used\n"


def evaluate_csv(rows: list[str]):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "input.csv"
        path.write_text(HEADER + "\n".join(rows) + "\n", encoding="utf-8")
        return evaluate(path)


class MPreEvaluatorTests(unittest.TestCase):
    def test_green_when_two_of_three_sessions_pass(self):
        gate, results = evaluate_csv([
            "S1,A,45,50,48,1,false,2,true,true,false",
            "S2,B,60,42,55,2,false,1,false,true,false",
            "S3,A,20,25,30,1,false,0,false,true,false",
        ])
        self.assertEqual("GREEN", gate)
        self.assertEqual(2, sum(item["green"] for item in results))

    def test_red_is_valid_when_only_one_session_passes(self):
        gate, results = evaluate_csv([
            "S1,A,50,50,50,1,false,0,false,true,false",
            "S2,B,50,50,50,0,false,0,false,true,false",
            "S3,A,50,50,50,1,true,0,false,true,false",
        ])
        self.assertEqual("RED", gate)
        self.assertEqual(1, sum(item["green"] for item in results))

    def test_rejects_single_pair(self):
        with self.assertRaises(ValueError):
            evaluate_csv([
                "S1,A,50,50,50,1,false,0,false,true,false",
                "S2,A,50,50,50,1,false,0,false,true,false",
                "S3,A,50,50,50,1,false,0,false,true,false",
            ])

    def test_rejects_non_human_or_gift_recipient(self):
        with self.assertRaises(ValueError):
            evaluate_csv([
                "S1,A,50,50,50,1,false,0,false,false,false",
                "S2,B,50,50,50,1,false,0,false,true,false",
                "S3,A,50,50,50,1,false,0,false,true,false",
            ])
        with self.assertRaises(ValueError):
            evaluate_csv([
                "S1,A,50,50,50,1,false,0,false,true,true",
                "S2,B,50,50,50,1,false,0,false,true,false",
                "S3,A,50,50,50,1,false,0,false,true,false",
            ])


if __name__ == "__main__":
    unittest.main()
