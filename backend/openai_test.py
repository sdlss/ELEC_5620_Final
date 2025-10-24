r"""
openai_test.py
Note: Minimal connectivity test using OPENAI_API_KEY.

In .env, set:
    OPENAI_API_KEY=sk-...
    # OPENAI_MODEL=gpt-5-nano
"""

import os
import sys

_CURRENT_DIR = os.path.dirname(__file__)
_PROJECT_ROOT = os.path.dirname(_CURRENT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from backend.config import get_settings, get_chat_client


def main():
    s = get_settings()
    print("[OpenAI model]", s.openai_model)
    client, model = get_chat_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'pong' if you can read this."},
        ],
    )
    print("OK:", resp.choices[0].message.content if resp.choices else "")


if __name__ == "__main__":
    main()
