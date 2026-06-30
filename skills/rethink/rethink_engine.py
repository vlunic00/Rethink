import json
import os


CRITIC_MODEL = "gpt-4o-mini"
GENERATION_MODEL = "gpt-4o"
MAX_TIMELINE_MESSAGES = 80
MAX_SNIPPET_CHARS = 250


def execute_rethink_command(
    chat_history,
    client=None,
    critic_model=CRITIC_MODEL,
    generation_model=GENERATION_MODEL,
):
    """Return a fresh response after pruning failed context and banning the bad path."""
    _validate_chat_history(chat_history)
    client = client or _default_client()

    analysis = _analyze_history(client, chat_history, critic_model)
    rollback_index = _rollback_index(analysis, len(chat_history))
    pivoted_payload = _pivoted_payload(chat_history, rollback_index, analysis)

    final_generation = client.chat.completions.create(
        model=generation_model,
        messages=pivoted_payload,
        temperature=0.85,
    )
    return _message_content(final_generation)


def _default_client():
    from openai import OpenAI

    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def _validate_chat_history(chat_history):
    if not isinstance(chat_history, list) or not chat_history:
        raise ValueError("chat_history must be a non-empty list")
    for index, message in enumerate(chat_history):
        if not isinstance(message, dict):
            raise ValueError(f"chat_history[{index}] must be a dict")
        if not isinstance(message.get("role"), str) or not message["role"]:
            raise ValueError(f"chat_history[{index}].role must be a non-empty string")
        if not isinstance(message.get("content"), str):
            raise ValueError(f"chat_history[{index}].content must be a string")


def _format_timeline(chat_history):
    start = max(0, len(chat_history) - MAX_TIMELINE_MESSAGES)
    lines = []
    for index, message in enumerate(chat_history[start:], start):
        snippet = message["content"][:MAX_SNIPPET_CHARS].replace("\n", " ")
        lines.append(f"Index [{index}] - {message['role'].upper()}: {snippet}...")
    return "\n".join(lines)


def _analyze_history(client, chat_history, critic_model):
    critic_prompt = f"""
You are the system middleware engineer for an AI execution pipeline.
The user triggered /rethink because the assistant is trapped optimizing a flawed, cyclical, or dead-end logic path.

Examine the chronological chat log timeline below. Identify the exact index where this specific technical approach, flawed logic loop, or assumption was first introduced.

TIMELINE LOGS:
{_format_timeline(chat_history)}

TASK:
1. Identify the rollback_index. This is the index of the message where the goal was stated right before the logic derailed.
2. Define the core_objective of that specific prompt.
3. Define the failed_approach that the assistant kept trying to optimize, which must now be banned.

Respond strictly using this JSON structure:
{{
  "rollback_index": int,
  "core_objective": "string summary",
  "failed_approach": "string describing the technical dead end"
}}
"""
    try:
        response = client.chat.completions.create(
            model=critic_model,
            messages=[{"role": "user", "content": critic_prompt}],
            response_format={"type": "json_object"},
        )
        raw = json.loads(_message_content(response))
    except (TypeError, ValueError, json.JSONDecodeError, AttributeError, KeyError):
        raw = {}

    return {
        "rollback_index": raw.get("rollback_index", max(0, len(chat_history) - 3)),
        "core_objective": _string_or_default(raw.get("core_objective"), "Satisfy the user's request."),
        "failed_approach": _string_or_default(raw.get("failed_approach"), "the prior dead-end strategy"),
    }


def _rollback_index(analysis, history_length):
    try:
        index = int(analysis["rollback_index"])
    except (TypeError, ValueError, KeyError):
        index = max(0, history_length - 3)
    return min(max(index, 0), history_length - 1)


def _pivoted_payload(chat_history, rollback_index, analysis):
    rethink_directive = f"""
[SYSTEM INSTRUCTION: /RETHINK TRIGGERED - ALTERNATIVE ROUTE MANDATE]
You are rolling back to this point in the timeline because your subsequent attempts hit an optimization rut.

Original Goal: "{analysis['core_objective']}".

EXECUTION PARADIGM SHIFT:
1. You are strictly forbidden from attempting this strategy or approach again: "{analysis['failed_approach']}".
2. Do not mention that a rollback occurred, do not apologize, and do not say "Let's try a different way".
3. Immediately execute a structurally different solution path to fulfill the request from this specific point in time.
"""
    return chat_history[: rollback_index + 1] + [{"role": "system", "content": rethink_directive}]


def _string_or_default(value, default):
    return value if isinstance(value, str) and value.strip() else default


def _message_content(response):
    return response.choices[0].message.content


def _self_check():
    class Message:
        def __init__(self, content):
            self.content = content

    class Choice:
        def __init__(self, content):
            self.message = Message(content)

    class Response:
        def __init__(self, content):
            self.choices = [Choice(content)]

    class Completions:
        def __init__(self):
            self.calls = []

        def create(self, **kwargs):
            self.calls.append(kwargs)
            if len(self.calls) == 1:
                return Response(json.dumps({
                    "rollback_index": 99,
                    "core_objective": "build the plugin",
                    "failed_approach": "retrying the same patch",
                }))
            return Response("fresh branch")

    class Chat:
        def __init__(self):
            self.completions = Completions()

    class FakeClient:
        def __init__(self):
            self.chat = Chat()

    client = FakeClient()
    result = execute_rethink_command(
        [
            {"role": "user", "content": "Build the plugin."},
            {"role": "assistant", "content": "Bad path."},
        ],
        client=client,
    )
    final_messages = client.chat.completions.calls[1]["messages"]
    assert result == "fresh branch"
    assert len(final_messages) == 3
    assert final_messages[-1]["role"] == "system"
    assert "retrying the same patch" in final_messages[-1]["content"]


if __name__ == "__main__":
    _self_check()
    print("self-check passed")
