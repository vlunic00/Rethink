# Rethink

Rethink helps an agent recover when a long conversation gets stuck optimizing the wrong approach.

It works in two layers:

- As a skill, it tells the agent to preserve the objective and valid constraints while continuing with a structurally different solution.
- As an optional Python engine, it can analyze a text chat history, build a replacement branch, and generate a fresh response.

## Invoke the skill

In Codex, explicitly invoke the skill with `$rethink` or select it through `/skills`. Phrases such as "rethink this" or "we're stuck" can also trigger it implicitly.

Hosts that expose skills as slash commands may use `/rethink` instead.

Skill-triggered behavior cannot replace a host's hidden active context. A host that supports real history replacement must call `build_rethink_branch(chat_history)` and install the returned message list itself.

## Install

For local Codex skill development, copy `skills/rethink` to `$HOME/.agents/skills/rethink`, then restart Codex if it does not appear automatically.

For plugin distribution, add the repository to a Codex plugin marketplace and install `rethink` from that marketplace. The Codex manifest is `.codex-plugin/plugin.json`; compatible Claude plugin hosts can use `.claude-plugin/plugin.json`.

## Python engine

The skill itself has no Python dependency. The optional engine requires the OpenAI Python SDK:

```powershell
python -m pip install openai
$env:OPENAI_API_KEY = "your-api-key"
```

`chat_history` must be a non-empty list containing at least one user message. Supported roles are `system`, `user`, and `assistant`, and every `content` value must be a string. Tool calls, tool results, and multimodal content are intentionally unsupported.

```python
from rethink import build_rethink_branch, execute_rethink_command

chat_history = [
    {"role": "user", "content": "Build the thing."},
    {"role": "assistant", "content": "Attempt one..."},
]

# Use this when the host owns inference and can replace its active history.
replacement_history = build_rethink_branch(chat_history)

# Use this when only the new assistant response is needed.
response = execute_rethink_command(chat_history)
```

The defaults are `gpt-5.6-luna` for analysis and `gpt-5.6` for generation. Compatible clients and model overrides can be passed explicitly:

```python
response = execute_rethink_command(
    chat_history,
    client=my_client,
    critic_model="gpt-5.6-luna",
    generation_model="gpt-5.6",
)
```

## Validate

The bundled check uses a fake client and does not require the SDK, an API key, or network access:

```powershell
python skills/rethink/rethink_engine.py
python -m compileall -q .
python -m json.tool .codex-plugin/plugin.json *> $null
python -m json.tool .claude-plugin/plugin.json *> $null
```

Run a separate API smoke test before changing models or request parameters.
