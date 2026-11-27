"""Structured event logger with real-time console streaming.

Every agent action (tool calls, model messages, approvals, errors) is
appended as a JSON line to an event log and streamed to the console so the
user can watch the agent work in real time. The model's reasoning is also
written to a dedicated reasoning log for audit and replay.
"""
import json
import os
from datetime import datetime, timezone

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
EVENT_LOG = os.path.join(LOG_DIR, "agent.jsonl")
REASONING_LOG = os.path.join(LOG_DIR, "reasoning.jsonl")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AgentLogger:
    def __init__(self, event_log=EVENT_LOG, reasoning_log=REASONING_LOG, stream_to_console=True):
        self.event_log = event_log
        self.reasoning_log = reasoning_log
        self.stream_to_console = stream_to_console
        os.makedirs(LOG_DIR, exist_ok=True)
        for path in (self.event_log, self.reasoning_log):
            if not os.path.exists(path):
                open(path, "a", encoding="utf-8").close()

    def _append(self, path, record):
        line = json.dumps(record, ensure_ascii=False)
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def stream(self, message):
        if self.stream_to_console:
            print(message, flush=True)

    def log(self, event_type, data=None):
        record = {"t": _now_iso(), "event": event_type}
        if data is not None:
            record["data"] = data
        self._append(self.event_log, record)
        preview = json.dumps(data, ensure_ascii=False) if data is not None else ""
        self.stream(f"[{event_type}] {preview}")
        return record

    def log_reasoning(self, text, source="model"):
        record = {"t": _now_iso(), "source": source, "reasoning": text}
        self._append(self.reasoning_log, record)
        self.stream(f"[reasoning:{source}] {text}")
        return record

    def log_tool_call(self, name, args):
        return self.log("tool_call", {"tool": name, "args": args})

    def log_tool_result(self, name, result, ok=True):
        return self.log("tool_result", {"tool": name, "ok": ok, "result": result})

    def log_model_message(self, role, content, tool_calls=None):
        data = {"role": role, "content": content}
        if tool_calls:
            data["tool_calls"] = [
                {"name": tc.function.name, "arguments": tc.function.arguments}
                for tc in tool_calls
            ]
        self.log("model_message", data)
        # The reasoning log captures the model's own words and tool choices.
        if content:
            self.log_reasoning(content, source=role)
        if tool_calls:
            for tc in tool_calls:
                self.log_reasoning(
                    f"→ calls tool {tc.function.name}({tc.function.arguments})",
                    source=role,
                )

    def log_approval(self, granted, reason=""):
        return self.log("approval", {"granted": granted, "reason": reason})

    def log_error(self, where, error):
        return self.log("error", {"where": where, "error": str(error)})