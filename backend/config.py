"""
config.py
说明：集中管理后端配置与环境变量。
- 读取 Azure OpenAI 所需环境变量
- 提供获取 AzureOpenAI 客户端与部署名的辅助函数

环境变量：
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_API_VERSION（例如 2024-07-18）
- AZURE_OPENAI_DEPLOYMENT（在 Studio 部署时自定义的 deployment name）
"""

import os
from functools import lru_cache
from typing import Tuple
from openai import AzureOpenAI


class Settings:
	azure_api_key: str
	azure_endpoint: str
	azure_api_version: str
	azure_deployment: str

	def __init__(self) -> None:
		self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
		self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
		self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-07-18").strip()
		self.azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()

	def validate(self):
		missing = []
		if not self.azure_api_key:
			missing.append("AZURE_OPENAI_API_KEY")
		if not self.azure_endpoint:
			missing.append("AZURE_OPENAI_ENDPOINT")
		if not self.azure_api_version:
			missing.append("AZURE_OPENAI_API_VERSION")
		if not self.azure_deployment:
			missing.append("AZURE_OPENAI_DEPLOYMENT")
		if missing:
			raise RuntimeError(f"缺少必要环境变量: {', '.join(missing)}")


@lru_cache()
def get_settings() -> Settings:
	return Settings()


def get_azure_openai_client() -> Tuple[AzureOpenAI, str]:
	"""返回 AzureOpenAI 客户端与部署名。"""
	s = get_settings()
	s.validate()
	client = AzureOpenAI(
		api_key=s.azure_api_key,
		api_version=s.azure_api_version,
		azure_endpoint=s.azure_endpoint,
	)
	return client, s.azure_deployment
