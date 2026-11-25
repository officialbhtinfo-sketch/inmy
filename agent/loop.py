import json
from openai import OpenAI
from .tools import TOOLS, dispatch


def make_client(base_url: str) -> OpenAI:
    return OpenAI(base_url=base_url, api_key="local")


def model_id(client: OpenAI) -> str:
    """Get the running model ID from llama-server."""
    try:
        return client.models.list().data[0].id
    except Exception:
        return "local"


def run_turn(client, model, messages, max_rounds=12) -> str:
    """Run one user turn, allowing the model to call tools when needed."""

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

        # No tool calls: the model has given its final answer.
        if not msg.tool_calls:
            answer = msg.content or ""
            messages.append({"role": "assistant", "content": answer})
            return answer

        messages.append(msg)

        images = []
        for tc in msg.tool_calls:
            name = tc.function.name

            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            print(f"  -> {name} {json.dumps(args, ensure_ascii=False)[:200]}")

            try:
                if not isinstance(args, dict):
                    raise ValueError("Tool arguments must be a JSON object")
                result = dispatch(name, args)
            except Exception as exc:
                result = {"content": f"Tool {name} failed: {exc}"}

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
    return answer
