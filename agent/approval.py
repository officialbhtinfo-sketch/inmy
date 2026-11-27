"""Approval manager: one user OK covers the agent for 30 minutes.

After 30 minutes of autonomous action the agent must ask for permission
again. The approval state is persisted to disk so it survives restarts.
"""
import json
import os
import time

STATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
STATE_FILE = os.path.join(STATE_DIR, "approval_state.json")
DEFAULT_INTERVAL_SECONDS = 30 * 60  # 30 minutes


class ApprovalManager:
    def __init__(self, interval_seconds=DEFAULT_INTERVAL_SECONDS, state_file=STATE_FILE):
        self.interval_seconds = interval_seconds
        self.state_file = state_file
        os.makedirs(STATE_DIR, exist_ok=True)
        self._state = self._load()

    def _load(self):
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"approved_at": 0}

    def _save(self):
        tmp = self.state_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._state, f)
        os.replace(tmp, self.state_file)

    def is_approved(self):
        """True if the current approval is still within the time window."""
        if not self._state.get("approved_at"):
            return False
        return (time.time() - self._state["approved_at"]) < self.interval_seconds

    def time_remaining(self):
        """Seconds left in the current approval window (0 if expired)."""
        if not self.is_approved():
            return 0
        return int(self.interval_seconds - (time.time() - self._state["approved_at"]))

    def request_approval(self, prompt="Agent needs permission to act for the next 30 minutes. Approve? [y/N] "):
        """Prompt the user once. Records the approval timestamp if granted."""
        try:
            answer = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            answer = "n"
        granted = answer == "y"
        if granted:
            self._state["approved_at"] = time.time()
            self._save()
        return granted

    def record_approval(self):
        """Mark as approved now (e.g. after a startup OK)."""
        self._state["approved_at"] = time.time()
        self._save()

    def revoke(self):
        self._state["approved_at"] = 0
        self._save()


# Module-level instance so tools can use it without threading it everywhere.
approval = ApprovalManager()


def is_approved():
    return approval.is_approved()


def request_approval(prompt=None):
    return approval.request_approval(prompt or "Agent needs permission to act for the next 30 minutes. Approve? [y/N] ")