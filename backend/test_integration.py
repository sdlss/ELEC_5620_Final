import asyncio
import os
from ocr_utils import extract_receipt_info
from issue_classifier import classify_issue

async def test_integration():
    # Get correct path for test image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "scanned-receipt-example.webp")
    
    # Verify file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Test receipt image not found at: {image_path}")
    
    print(f"\nTesting Receipt Extraction from: {image_path}")
    try:
        # Test OCR
        receipt_data = extract_receipt_info(image_path)
        print(f"OCR Results: {receipt_data}")

        # Test Classification
        issue_desc = "The phone I ordered arrived with a cracked screen and missing accessories"
        classification = await classify_issue(issue_desc)
        print(f"Classification Results: {classification}")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_integration())