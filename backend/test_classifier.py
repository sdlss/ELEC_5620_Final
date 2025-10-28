import json
import asyncio
from issue_classifier import classify_issue

async def test_classification():
    test_cases = [
        "My order never arrived and it's been 2 weeks",
        "The phone arrived with a cracked screen in the box",
        "I ordered a blue shirt but received a red one",
        "I want a refund, this product doesn't work as advertised",
        "The warranty card says 2 years but it stopped working after 6 months"
    ]
    
    for issue in test_cases:
        print(f"\nTesting issue: {issue}")
        result = await classify_issue(issue)
        print(f"Classification: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_classification())