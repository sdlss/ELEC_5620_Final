"""
ai_agent.py
说明：仅使用 OpenAI 公共 API 的最小交互逻辑。
"""

from typing import Dict
from .config import get_chat_client


def analyze_issue(issue_description: str) -> Dict:
	"""最小分析：基于描述生成要点与建议。"""
	client, model = get_chat_client()

	system_prompt = (
		"你是一个电商售后维权助手。基于用户提供的问题描述，"
		"用简洁的语言给出问题要点总结和下一步建议。"
	)

	user_prompt = f"问题描述：\n{issue_description}\n\n请输出：\n1) 问题要点\n2) 建议步骤(3条以内)"

	resp = client.chat.completions.create(
		model=model,
		messages=[
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": user_prompt},
		],
	)
	content = resp.choices[0].message.content if resp.choices else ""

	return {
		"model": model,
		"issue_description": issue_description,
		"analysis": content,
	}


