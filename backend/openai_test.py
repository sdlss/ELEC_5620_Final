r"""
openai_test.py
说明：使用 OPENAI_API_KEY 做最小连通性测试。

在 .env 写：
  OPENAI_API_KEY=sk-...
  # 可选：OPENAI_MODEL=gpt-4o-mini（默认）
  # 可选：OPENAI_BASE_URL=自定义基地址（通常不需要）

运行（Windows cmd，模块方式）：
  D:\anaconda\Scripts\conda.exe run -p d:\Desktop\ELEC_5620_Final\.conda --no-capture-output python -m backend.openai_test
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
