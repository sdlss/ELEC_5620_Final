"""
ai_agent.py
说明：封装与 Azure OpenAI 的最小交互逻辑。
当前实现：给定 issue_description，生成简要分析与建议。
后续可扩展：串联 prompts（收据抽取/问题分析/政策/话术）。
"""

from typing import Dict
from .config import get_azure_openai_client


def analyze_issue(issue_description: str) -> Dict:
	"""使用 Azure OpenAI 进行最小分析，返回结构化结果。"""
	client, deployment = get_azure_openai_client()

	system_prompt = (
		"你是一个电商售后维权助手。基于用户提供的问题描述，"
		"用简洁的语言给出问题要点总结和下一步建议。"
	)

	user_prompt = f"问题描述：\n{issue_description}\n\n请输出：\n1) 问题要点\n2) 建议步骤(3条以内)"

	resp = client.chat.completions.create(
		model=deployment,
		messages=[
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": user_prompt},
		],
		temperature=0.3,
	)
	content = resp.choices[0].message.content if resp.choices else ""

	return {
		"issue_description": issue_description,
		"analysis": content,
	}
