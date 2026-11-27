import os
import json
import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent.logger import AgentLogger


class LoggerTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.event_log = os.path.join(self.tmpdir, "events.jsonl")
        self.reasoning_log = os.path.join(self.tmpdir, "reasoning.jsonl")
        self.log = AgentLogger(
            event_log=self.event_log,
            reasoning_log=self.reasoning_log,
            stream_to_console=False,
        )

    def _read(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def test_log_event_writes_json_line(self):
        self.log.log("tool_call", {"tool": "shell", "args": {"command": "ls"}})
        events = self._read(self.event_log)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "tool_call")
        self.assertEqual(events[0]["data"]["tool"], "shell")
        self.assertIn("t", events[0])

    def test_log_reasoning_writes_to_reasoning_file(self):
        self.log.log_reasoning("I should check the file first.", source="model")
        records = self._read(self.reasoning_log)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["reasoning"], "I should check the file first.")
        self.assertEqual(records[0]["source"], "model")

    def test_log_model_message_logs_content_and_reasoning(self):
        calls = []
        self.log.log_model_message("assistant", "Let me search.", tool_calls=calls)
        events = self._read(self.event_log)
        reasoning = self._read(self.reasoning_log)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "model_message")
        self.assertEqual(len(reasoning), 1)
        self.assertEqual(reasoning[0]["reasoning"], "Let me search.")

    def test_log_tool_call_and_result(self):
        self.log.log_tool_call("web_search", {"query": "x"})
        self.log.log_tool_result("web_search", {"content": "results"}, ok=True)
        events = self._read(self.event_log)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event"], "tool_call")
        self.assertEqual(events[1]["event"], "tool_result")
        self.assertTrue(events[1]["data"]["ok"])

    def test_log_approval_and_error(self):
        self.log.log_approval(True)
        self.log.log_error("shell", ValueError("boom"))
        events = self._read(self.event_log)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event"], "approval")
        self.assertEqual(events[1]["event"], "error")
        self.assertIn("boom", events[1]["data"]["error"])

    def test_stream_disabled_prints_nothing(self):
        # stream_to_console=False; just ensure no exception and files written
        self.log.log("event", {"x": 1})
        self.log.log_reasoning("r")
        self.log.log_tool_call("t", {})
        self.log.log_tool_result("t", {"content": "ok"})
        self.log.log_approval(True)
        self.log.log_error("where", ValueError("boom"))
        self.assertTrue(os.path.exists(self.event_log))
        self.assertTrue(os.path.exists(self.reasoning_log))


if __name__ == "__main__":
    unittest.main()