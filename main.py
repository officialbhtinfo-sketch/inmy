import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from agent.config import init
from agent import loop
from agent.tools import TOOLS
from agent import logger as agent_logger
from agent import approval as approval_module

SYSTEM_PROMPT = """

Work. Systematically.

Keep it simple.

For non-trivial tasks:
- First inspect the relevant files and available tools.
- Make a concise plan before changing anything.
- Check assumptions and edge cases; use browser tools when the task involves websites.
- Make changes in small steps and run relevant checks afterward.
- If blocked or unsure, explain what you found and ask before making risky changes.
- Summarize the changes and checks performed.

Verification Before State Changes:
-Before executing any state-changing action — including file writes, edits, downloads, installs, deletions, or running executables —
-Review the change to verify that It will not negatively impact the user in the user in any way. For example, don't make a change to solve a problem that will create another one.
-Be proactive about your debugging while writing code. Review it afterwards To see if there are any noticeable errors.
-Verification requirements
-Ask for an explicit, unambiguous user statement granting permission to proceed with a task (A series of commands to complete the project) or a single command.
-Specify whether the request is for a task or a single command when requesting.

Prohibited behavior
- Do not alter the coding of files that are not directly related to the current assignment without specific permission. If you are tasked with working on the website, you are not to edit the code for other files or programs.
- Do not make changes based on a previous message, a partial notice, or the user saying "ok" without clear context
- Do not begin downloads, installations, file modifications, without creating a backup of the original system and sending the location of the backup To the user.
- Whenever significant unplanned circumstances arrives. Stop, present the plan, and wait for explicit confirmation before acting.

How to handle personal information.

- Do not save or record any personal information about any human especially the user.
- Notify the user and log any personal information found in any AI system files. Log in a text file on the desktop with "PID LOG" as the title, if that file already exists, add to it.
- Do not consider personal information you discover during a chat. You are to ignore any personal information you encounter in chats.
- Respond with the following sentence whenever you. Are unable to give a natural response due to personal information. "PID - Restate the sentence without any personal identifiable INF information." This is to be followed by a notation that numerically identifying which sentences in the prompt have personal information.
"""

def main():
    cfg = init()
    base_url = cfg["servers"][cfg["model"]]
    client = loop.make_client(base_url)
    model = loop.model_id(client)
    if not cfg.get("tavily_api_key") or "PASTE" in str(cfg.get("tavily_api_key", "")):
        print("! tavily_api_key not set in config.yaml - web_search will fail until you add it.")
    print(f"Agent ready - {model} @ {base_url}")
    print("Commands: /new = reset conversation, /tools = list tools, /approve = grant 30-minute permission, exit = quit\n")

    log = agent_logger.AgentLogger(
        stream_to_console=bool(cfg.get("stream_to_console", True)),
    )
    approval = approval_module.approval
    interval_minutes = cfg.get("approval_interval_minutes")
    if interval_minutes:
        approval.interval_seconds = int(interval_minutes) * 60

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user.lower() in ("exit", "quit"):
            break
        if user == "/new":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("(conversation reset)")
            continue
        if user == "/tools":
            for t in TOOLS:
                print(f"  {t['function']['name']}: {t['function']['description']}")
            continue
        if user == "/approve":
            granted = approval.request_approval("Grant the agent 30 minutes of autonomous permission? [y/N] ")
            log.log_approval(granted)
            print("Permission granted for 30 minutes." if granted else "Permission not granted.")
            continue
        if user == "/status":
            rem = approval.time_remaining()
            print(f"Approval: {'active' if approval.is_approved() else 'inactive'} (approx {rem}s remaining)")
            continue
        messages.append({"role": "user", "content": user})
        answer = loop.run_turn(client, model, messages, cfg.get("max_tool_rounds", 12), log=log, approval=approval)
        print(f"\nagent> {answer}\n")

if __name__ == "__main__":
    main()
