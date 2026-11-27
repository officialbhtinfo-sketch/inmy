import os
import json
import time
import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent.approval import ApprovalManager


class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.tmpdir, "approval_state.json")

    def make(self, interval_seconds=1):
        return ApprovalManager(interval_seconds=interval_seconds, state_file=self.state_file)

    def test_not_approved_initially(self):
        m = self.make()
        self.assertFalse(m.is_approved())

    def test_request_approval_granted_sets_window(self):
        m = self.make(interval_seconds=60)
        with patch('builtins.input', return_value='y'):
            self.assertTrue(m.request_approval())
        self.assertTrue(m.is_approved())
        self.assertGreater(m.time_remaining(), 0)
        # state persisted
        with open(self.state_file) as f:
            state = json.load(f)
        self.assertIn("approved_at", state)

    def test_request_approval_refused(self):
        m = self.make(interval_seconds=60)
        with patch('builtins.input', return_value='n'):
            self.assertFalse(m.request_approval())
        self.assertFalse(m.is_approved())

    def test_approval_expires_after_interval(self):
        m = self.make(interval_seconds=1)
        with patch('builtins.input', return_value='y'):
            m.request_approval()
        self.assertTrue(m.is_approved())
        time.sleep(1.1)
        self.assertFalse(m.is_approved())
        self.assertEqual(m.time_remaining(), 0)

    def test_revoke(self):
        m = self.make(interval_seconds=60)
        with patch('builtins.input', return_value='y'):
            m.request_approval()
        self.assertTrue(m.is_approved())
        m.revoke()
        self.assertFalse(m.is_approved())

    def test_record_approval_without_prompt(self):
        m = self.make(interval_seconds=60)
        m.record_approval()
        self.assertTrue(m.is_approved())


if __name__ == "__main__":
    unittest.main()