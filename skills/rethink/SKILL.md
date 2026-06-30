---
name: rethink
description: Use when the user invokes /rethink, asks to rethink this, says the conversation is stuck, or wants a hard pivot away from a failed approach. Performs surgical backtracking from visible context, injects a negative constraint against the failed strategy, and continues with a structurally different solution path.
---

# Rethink

When triggered, stop optimizing the current failed path.

1. Identify the earliest visible point where the flawed technical strategy or assumption entered the conversation.
2. Preserve the user's original objective from just before that derailment.
3. Name the failed approach internally and do not repeat it.
4. Continue immediately with a different structure, algorithm, tool path, or implementation strategy.

Do not announce that a rollback occurred. Do not apologize. Do not say "let's try a different way." Just execute the new path.

For hosts that can pass and replace a real chat-history array, use `rethink_engine.py` to perform model-assisted rollback and fresh generation.
