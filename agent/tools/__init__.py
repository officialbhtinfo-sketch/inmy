from .web_search import web_search
from .web_fetch import web_fetch
from .screenshot import screenshot
from .shell import shell
from .memory import memory_save, memory_search, memory_list
from .. import approval
from .. import config

TOOLS = [
    {"type": "function", "function": {
        "name": "web_search",
        "description": "Search the web for current information, news, facts, or anything you don't know. Use this FIRST when the user asks about something factual, current, or you need to look up information. Returns top results with titles, URLs and snippets.",
        "parameters": {"type": "object",
            "properties": {"query": {"type": "string", "description": "Search query"}},
            "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "web_fetch",
        "description": "Read the full content of a specific web page URL. Use AFTER web_search to read a promising result in full.",
        "parameters": {"type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"]}}},
    {"type": "function", "function": {
        "name": "screenshot",
        "description": "Capture the user's screen as an image. Use when the user refers to what is on their screen, a dialog, window, error message, or their desktop.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "shell",
        "description": "Run a command on the user's Windows machine (PowerShell) and get its output. Use ONLY when the user explicitly asks you to run a command or manage files on their computer. Prefer read-only commands. NOT for looking up facts or information.",
        "parameters": {"type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"]}}},
    {"type": "function", "function": {
        "name": "memory_save",
        "description": "Save a durable fact to long-term memory. Use when you learn something worth remembering across sessions: user preferences, project details, file paths, decisions made, ongoing tasks. Do NOT save trivia or one-off conversation.",
        "parameters": {"type": "object",
            "properties": {
                "key": {"type": "string", "description": "Short unique id, e.g. 'project_opwin_stack'"},
                "text": {"type": "string", "description": "The fact to remember, one or two sentences."},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional tags like 'website', 'preference', 'project'"}},
            "required": ["key", "text"]}}},
    {"type": "function", "function": {
        "name": "memory_search",
        "description": "Search long-term memory for relevant facts. Call this at the START of any task involving the user's projects, preferences, or prior work, BEFORE acting.",
        "parameters": {"type": "object",
            "properties": {"query": {"type": "string", "description": "What to look for"}},
            "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "memory_list",
        "description": "List all saved memories. Use sparingly; prefer memory_search.",
        "parameters": {"type": "object", "properties": {}}}},
]


def dispatch(name: str, args: dict) -> dict:
    """Run a tool. Returns {'content': str, 'image_b64': str | None}."""
    if name == "web_search":
        return {"content": web_search(args.get("query", ""))}
    if name == "web_fetch":
        return {"content": web_fetch(args.get("url", ""))}
    if name == "screenshot":
        r = screenshot()
        return {"content": f"Screenshot captured ({r['w']}x{r['h']}). Attached as an image.",
                "image_b64": r["b64"]}
    if name == "shell":
        if not config.CFG.get("allow_shell", False):
            return {"content": "Shell tool is disabled (allow_shell: false in config.yaml)."}
        cmd = args.get("command", "")
        # Gate shell on the 30-minute approval window: one user OK covers the
        # agent for the next 30 minutes of autonomous action.
        if not approval.is_approved():
            granted = approval.request_approval(
                f"Agent wants to run a shell command:\n    {cmd}\nApprove for the next 30 minutes? [y/N] "
            )
            if not granted:
                return {"content": "The user refused to run this command. Do not retry it; ask what they would like instead."}
        return {"content": shell(cmd)}
    if name == "memory_save":
        return {"content": memory_save(args.get("key", ""), args.get("text", ""), args.get("tags") or [])}
    if name == "memory_search":
        return {"content": memory_search(args.get("query", ""))}
    if name == "memory_list":
        return {"content": memory_list()}
    return {"content": f"Unknown tool: {name}"}