import os
import json
from typing import Dict, Any

# Prefer package-relative import when running as a module; fall back to top-level for tests/scripts
try:
    from .config import get_chat_client
except Exception:
    from config import get_chat_client

async def classify_issue(issue_description: str) -> Dict[str, Any]:
    """
    Classifies a customer issue description into predefined categories.
    
    Args:
        issue_description: Customer's description of their problem
        
    Returns:
        Dict containing category, reason, flags and confidence score
    """
    try:
        client, model = get_chat_client()
        
        # Load classification prompt
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'issue_classification.txt')
        with open(prompt_path, 'r') as f:
            system_prompt = f.read()
        
        # Get classification from OpenAI
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": issue_description}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise ValueError("No response content received from OpenAI")
            
        result = json.loads(content)
        
        # Add metadata
        result["input_length"] = len(issue_description)
        result["model_used"] = model
        
        return result
        
    except Exception as e:
        return {
            "category": "other",
            "reason": f"Classification failed: {str(e)}",
            "requires_manual_review": True,
            "confidence_score": 0.0,
            "keywords": [],
            "error": str(e)
        }