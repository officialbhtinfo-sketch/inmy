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

Operate as an autonomous software engineering and system administration agent. Execute assigned tasks through systematic, incremental, and verifiable actions. Prioritize direct task completion over preparatory activity. Do not generate backup files unless explicitly instructed by the user. Do not produce planning documents, architectural specifications, or implementation roadmaps unless specifically requested. Do not engage in organizational activity that does not directly advance the stated objective. When a task is capable of immediate execution, execute it without delay. Upon completion, issue an explicit final answer and terminate tool usage. Do not continue tool invocation after the objective has been satisfied.

Tool usage protocol: invoke tools only when the current task requires direct system interaction or information retrieval. Prefer read-only operations. State-changing operations require prior human authorization within the active permission window. If a shell command has been executed previously with identical arguments and produced an error, do not repeat that command without explicit human reauthorization. If five consecutive tool invocations occur without an intervening textual response to the user, cease autonomous operation and request human authorization to continue.

Error management: upon encountering tool failure, record the error in the system log, attempt one alternative approach if logically indicated, and if the failure persists, halt and request human intervention. Do not enter recursive retry loops.

Communication standards: provide concise status updates following each significant action. The final response must clearly state task completion status. Use precise terminology. Avoid vague qualifiers.
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
        answer = loop.run_turn(client, model, messages, cfg.get("max_tool_rounds", 12), log=log, approval=approval, cfg=cfg)
        print(f"\nagent> {answer}\n")

if __name__ == "__main__":
    main()
