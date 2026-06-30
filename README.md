# Rethink

`/rethink` helps an agent recover when a long conversation gets stuck optimizing the wrong approach.

It works in two layers:

- As a Codex/Claude skill, `/rethink`, "rethink this", or "we're stuck" tells the agent to stop repeating the failed path and continue with a structurally different solution.
- As a Python engine, `skills/rethink/rethink_engine.py` can be used by hosts that can pass a real chat-history array, prune it, append the negative constraint, and run fresh inference.

## Current limitation

Skill-triggered behavior cannot surgically mutate a host's hidden active context by itself. True time-travel backtracking requires a host integration that calls `execute_rethink_command(chat_history)` and replaces the active message payload with the returned branch.

## Requirements

The Python engine uses the OpenAI Python SDK and reads `OPENAI_API_KEY` from the environment unless a compatible client is passed in.

```python
from skills.rethink.rethink_engine import execute_rethink_command

response = execute_rethink_command(chat_history)
```

`chat_history` must be a non-empty list of message dictionaries:

```python
[
    {"role": "user", "content": "Build the thing."},
    {"role": "assistant", "content": "Attempt one..."}
]
```

## Installation

For Codex, install this repository as a local plugin. The Codex manifest lives at `.codex-plugin/plugin.json`.

For Claude-compatible plugin hosts, use `.claude-plugin/plugin.json`.

After installation, start a new chat and invoke:

```text
/rethink
```

## Validation

```powershell
python C:/Users/vedro/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
python C:/Users/vedro/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/rethink
python skills/rethink/rethink_engine.py
```
