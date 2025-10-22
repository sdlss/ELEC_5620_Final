"""
ai_agent.py
Description: Minimal interaction logic using the OpenAI public API only.
Enhancement: Ask the model to return structured JSON (key_points, steps),
and parse it with a safe fallback to plain text.
"""

from typing import Dict, Any, List
import json
from .config import get_chat_client




def analyze_issue(issue_description: str) -> Dict[str, Any]:
	"""
	Minimal analysis: summarize key points and next steps based on the description.
	Returns a dict that always includes:
	- model: str
	- issue_description: str
	- analysis: str (raw model text)
	And, when possible, also includes parsed fields:
	- key_points: List[str]
	- steps: List[str]
	"""
	client, model = get_chat_client()

	system_prompt = (
		"You are an e-commerce after-sales dispute assistant. Based on the user's issue description, "
		"provide a concise summary of the key points and actionable next-step suggestions."
	)

	user_prompt = (
		f"Issue description:\n{issue_description}\n\n"
		"Return ONLY a compact JSON object with the following structure and nothing else (no markdown):\n"
		"{\n"
		"  \"key_points\": [string],\n"
		"  \"steps\": [string]\n"
		"}\n"
		"- key_points: bullet points summarizing the core problems.\n"
		"- steps: up to 3 actionable next steps.\n"
	)

	resp = client.chat.completions.create(
		model=model,
		messages=[
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": user_prompt},
		],
	)
	content = resp.choices[0].message.content if resp.choices else ""

	# Try to parse the JSON shape { key_points: [...], steps: [...] }
	key_points: List[str] = []
	steps: List[str] = []
	if content:
		try:
			parsed = json.loads(content)
			if isinstance(parsed, dict):
				kp = parsed.get("key_points")
				st = parsed.get("steps")
				if isinstance(kp, list):
					key_points = [str(x) for x in kp if isinstance(x, (str, int, float))]
				if isinstance(st, list):
					steps = [str(x) for x in st if isinstance(x, (str, int, float))]
		except Exception:
			# Fallback: leave parsed fields empty and keep raw text in analysis
			pass

	return {
		"model": model,
		"issue_description": issue_description,
		"analysis": content,
		"key_points": key_points,
		"steps": steps,
	}


