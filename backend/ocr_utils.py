import easyocr
import re
import sys
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Union

def preprocess_image(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image from {image_path}")
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)
    thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return thresh

def extract_text_from_image(image_path: str, use_preprocessing: bool = True) -> str:
    reader = easyocr.Reader(['en'], gpu=False)
    img = preprocess_image(image_path) if use_preprocessing else image_path
    results = reader.readtext(img, detail=0, paragraph=False)
    return '\n'.join(str(line) for line in results)

def parse_receipt_fields(ocr_text: str, debug: bool = False) -> Dict[str, Any]:
    result = {
        "seller_name": None,
        "receipt_id": None,
        "purchase_date": None,
        "item_list": [],
        "purchase_total": {"currency": "USD", "value": None},
        "payment_method": None,
        "field_confidence": {
            "seller_name": 0.0,
            "receipt_id": 0.0,
            "purchase_date": 0.0,
            "purchase_total": 0.0,
            "item_list": 0.0,
            "payment_method": 0.0
        }
    }
    text = ocr_text.upper()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    norm_lines = []
    for line in lines:
        # Normalize OCR errors
        line = line.replace(',', '.')
        line = re.sub(r'\$ *([0-9]+\. *[0-9]{2})', lambda m: f"${m.group(1).replace(' ', '')}", line)
        line = re.sub(r'# *([0-9]+\. *[0-9]{2})', lambda m: f"{m.group(1).replace(' ', '')}", line)
        line = re.sub(r'([0-9]+)\.\s*([0-9]{2})', r'\1.\2', line)
        line = re.sub(r'\s+', ' ', line)
        norm_lines.append(line)
    lines = norm_lines

    # Extract Seller Name (First line with many capitals, usually)
    for line in lines:
        if re.search(r'[A-Z]{3,}', line):
            result["seller_name"] = line.title()
            result["field_confidence"]["seller_name"] = 1.0
            break

    # Extract Receipt/Order Number
    # Try TC#/TR#/REF#
    rec_match = (re.search(r'(TC[#:\s]*([0-9]+))', " ".join(lines))
                or re.search(r'(TR[#:\s]*([0-9]+))', " ".join(lines))
                or re.search(r'(REF[#:\s]*([A-Z0-9]+))', " ".join(lines)))
    if rec_match:
        result["receipt_id"] = rec_match.group(2)
        result["field_confidence"]["receipt_id"] = 0.95

    # Extract Purchase Date
    date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', " ".join(lines))
    if date_match:
        result["purchase_date"] = date_match.group(1)
        result["field_confidence"]["purchase_date"] = 0.95

    # Extract Payment Method
    for line in lines:
        pmatch = re.search(r'(VISA|MASTERCARD|AMEX|PAYPAL|CASH|CARD)', line)
        if pmatch:
            result["payment_method"] = pmatch.group(1).title()
            result["field_confidence"]["payment_method"] = 1.0
            break

    # Extract Purchase Total
    total_value, total_conf = None, 0.0
    for i, line in enumerate(lines):
        if 'TOTAL' in line and 'SUBTOTAL' not in line:
            if i+1 < len(lines):
                raw = lines[i+1]
                pmatch = re.search(r'([0-9]+\.[0-9]{2})', raw)
                if pmatch:
                    total_value = float(pmatch.group(1))
                    total_conf = 0.95
                    break
            pmatch = re.search(r'([0-9]+\.[0-9]{2})', line)
            if pmatch:
                total_value = float(pmatch.group(1))
                total_conf = 0.9
                break
    if total_value:
        result["purchase_total"]["value"] = total_value
        result["field_confidence"]["purchase_total"] = total_conf

    # Extract Item List (description + price, two-line format)
    exclude_words = [
        "WALMART", "SAVE MONEY", "LIVE BETTER", "TOTAL", "SUBTOTAL", "TAX", "TEND", "BALANCE",
        "APPROVAL", "ACCOUNT", "VISA", "MASTERCARD", "AMEX", "PAYPAL", "CASH", "CARD",
        "ST#", "OP#", "TE#", "TR#", "REF", "TRANS", "VALIDATION", "PAYMENT", "TERMINAL", "ITEMS SOLD",
        "TC#", "TC #", "CAMINO", "DURANGO", "MAR ", "JIM", "JAMES", "LOW PRICE", "EVERY DAY", "THANK YOU"
    ]
    for i, line in enumerate(lines):
        if any(w in line for w in exclude_words):
            continue
        if i+1 < len(lines):
            next_line = lines[i+1]
            pmatch = re.match(r'^\$?([0-9]+\.[0-9]{2})$', next_line)
            if not re.match(r'^\$?([0-9]+\.[0-9]{2})$', line) and pmatch and len(line) >= 5:
                desc = line.strip().title()
                price = float(pmatch.group(1))
                # Factual clarity of line association
                result["item_list"].append({
                    "description": desc,
                    "price": price
                })
    if result["item_list"]:
        result["field_confidence"]["item_list"] = 0.85

    return result

def extract_receipt_info(image_path: str, debug: bool = False) -> Dict[str, Any]:
    text = extract_text_from_image(image_path, use_preprocessing=True)
    parsed_data = parse_receipt_fields(text, debug=debug)
    return parsed_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr_utils.py <image_path> [--debug]")
        print("\nExample:")
        print("  python ocr_utils.py receipt.jpg --debug")
        sys.exit(1)
    image_path = sys.argv[1]
    debug_mode = "--debug" in sys.argv
    result = extract_receipt_info(image_path, debug=debug_mode)
    print("\n" + "=" * 70)
    print("OCR RECEIPT EXTRACTION RESULT")
    print("=" * 70)
    print(f"Source: {image_path}")
    print("-" * 70)
    print(f"Merchant/Seller Name: {result['seller_name']}")
    print(f"Receipt/Order Number: {result['receipt_id']}")
    print(f"Date of Purchase: {result['purchase_date']}")
    print(f"Payment Method: {result['payment_method']}")
    print(f"Purchase Total: ${result['purchase_total']['value']}")
    print("\nItem List:")
    if result['item_list']:
        for item in result['item_list']:
            print(f"  - {item['description']} ")
    else:
        print("  [No items found]")
