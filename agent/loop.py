import json
from openai import OpenAI
from .tools import TOOLS, dispatch
from . import logger as agent_logger
from . import approval as approval_module


def make_client(base_url: str) -> OpenAI:
    return OpenAI(base_url=base_url, api_key="local")


def model_id(client: OpenAI) -> str:
    """Get the running model ID from llama-server."""
    try:
        return client.models.list().data[0].id
    except Exception:
        return "local"


def run_turn(client, model, messages, max_rounds=12, log=None, approval=None) -> str:
    """Run one user turn, allowing the model to call tools when needed.

    `log` (AgentLogger) records every action and streams it in real time.
    `approval` (ApprovalManager) gates state-changing tools to a 30-minute
    permission window. When omitted, sensible defaults are created.
    """
    log = log or agent_logger.AgentLogger()
    approval = approval or approval_module.approval

    # Add the instruction once, without duplicating it on future turns.
    if not any(message.get("role") == "system" for message in messages):
        messages.insert(
            0,
            {
                "role": "system",
                "content": (
                    "Answer directly and concisely. Use tools only when needed. "
                    "For coding requests, provide the code first and keep the "
                    "explanation brief and relevant. Don't add unrelated ideas."
                    "Request permission to complete the entire task, instead of code by code, if there are no foreseeable risks"
                ),
            },
        )

    for _ in range(max_rounds):
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.2,
        )

        msg = resp.choices[0].message

        # Log + stream the model's reasoning/message before acting on it.
        log.log_model_message(getattr(msg, "role", None) or "assistant", msg.content or "", msg.tool_calls)

        # No tool calls: the model has given its final answer.
        if not msg.tool_calls:
            answer = msg.content or ""
            messages.append({"role": "assistant", "content": answer})
            log.log("final_answer", {"content": answer})
            return answer

        messages.append(msg)

        images = []
        for tc in msg.tool_calls:
            name = tc.function.name

            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            log.log_tool_call(name, args)

            try:
                if not isinstance(args, dict):
                    raise ValueError("Tool arguments must be a JSON object")
                result = dispatch(name, args)
                ok = True
            except Exception as exc:
                result = {"content": f"Tool {name} failed: {exc}"}
                ok = False
                log.log_error(name, exc)

            log.log_tool_result(name, result, ok=ok)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result.get("content", ""),
                }
            )

            # Pass a screenshot back to the model if the tool returned one.
            if result.get("image_b64"):
                images.append(
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "(screenshot attached)"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": (
                                        "data:image/png;base64,"
                                        f"{result['image_b64']}"
                                    )
                                },
                            },
                        ],
                    }
                )

        messages.extend(images)

    answer = "[stopped: hit max tool rounds]"
    messages.append({"role": "assistant", "content": answer})
    log.log("max_rounds_reached", {})
    return answer
