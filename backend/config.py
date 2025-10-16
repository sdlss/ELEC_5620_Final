"""
config.py (OpenAI only)
说明：仅使用 OpenAI 公共 API 的最小配置封装。
提供 get_chat_client() → (client, model)
"""

import os
from functools import lru_cache
from typing import Tuple

from dotenv import load_dotenv
from openai import OpenAI

# 自动加载 .env（若存在）
load_dotenv(override=False)


class Settings:
	openai_api_key: str
	openai_base_url: str
	openai_model: str

	def __init__(self) -> None:
		self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
		self.openai_base_url = os.getenv("OPENAI_BASE_URL", "").strip()
		self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"

	def validate(self):
		if not self.openai_api_key:
			raise RuntimeError("缺少 OPENAI_API_KEY")


@lru_cache()
def get_settings() -> Settings:
	return Settings()


def get_chat_client() -> Tuple[OpenAI, str]:
	s = get_settings()
	s.validate()
	if s.openai_base_url:
		client = OpenAI(api_key=s.openai_api_key, base_url=s.openai_base_url)
	else:
		client = OpenAI(api_key=s.openai_api_key)
	return client, s.openai_model

