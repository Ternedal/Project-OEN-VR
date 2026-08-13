#!/usr/bin/env python3
"""Static contract tests for the offline M-Pre facilitator runner.

These tests do not simulate a playtest and do not create evidence. They only ensure
that the browser helper remains offline, anonymous and compatible with evaluate_mpre.py.
"""
from __future__ import annotations

import ast
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

from evaluate_mpre import REQUIRED_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "prototype" / "m-pre" / "facilitator_runner.html"


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.remote_refs: list[str] = []
        self.task_cards = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.add(element_id)
        classes = set((values.get("class") or "").split())
        if "task" in classes:
            self.task_cards += 1
        for key in ("src", "href"):
            value = values.get(key)
            if value and value.startswith(("http://", "https://", "//")):
                self.remote_refs.append(value)


class MPreFacilitatorRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = RUNNER.read_text(encoding="utf-8")
        cls.parser = IdCollector()
        cls.parser.feed(cls.text)

    def test_runner_is_offline_only(self) -> None:
        self.assertEqual([], self.parser.remote_refs)
        self.assertNotIn("fetch(", self.text)
        self.assertNotIn("XMLHttpRequest", self.text)
        self.assertNotIn("WebSocket", self.text)

    def test_required_anonymous_fields_exist(self) -> None:
        required_ids = {
            "sessionId", "pairId", "humanSession", "giftRecipient",
            "regret", "administration", "saveSession", "exportCsv",
            "exportNotes", "clearBatch", "batchStatus", "revealStorm",
        }
        self.assertTrue(required_ids.issubset(self.parser.ids))
        self.assertNotRegex(self.text, r'id=["\'](?:tester|player).*name')

    def test_all_six_task_cards_are_present(self) -> None:
        self.assertEqual(6, self.parser.task_cards)
        for title in (
            "Skaf mad", "Forstærk ly", "Hold bål", "Byg signalbål",
            "Behandl skade", "Udforsk kysten",
        ):
            self.assertIn(title, self.text)

    def test_export_schema_matches_authoritative_evaluator(self) -> None:
        match = re.search(r"const FIELDS = (\[[^;]+\]);", self.text)
        self.assertIsNotNone(match, "Runner must declare CSV FIELDS")
        fields = ast.literal_eval(match.group(1))
        self.assertEqual(set(fields), REQUIRED_COLUMNS)
        self.assertEqual(len(fields), len(REQUIRED_COLUMNS))

    def test_runner_does_not_claim_to_decide_project_gate(self) -> None:
        self.assertIn("Den autoritative evaluator — ikke denne side — afgør den samlede M-Pre-gate.", self.text)
        self.assertNotIn("M-PRE GATE:", self.text)
        self.assertNotIn("gate = 'GREEN'", self.text)
        self.assertNotIn('gate = "GREEN"', self.text)

    def test_local_batch_and_download_are_explicit(self) -> None:
        self.assertIn("localStorage", self.text)
        self.assertIn("new Blob", self.text)
        self.assertIn("URL.createObjectURL", self.text)
        self.assertIn("mpre_sessions.csv", self.text)


if __name__ == "__main__":
    unittest.main()
