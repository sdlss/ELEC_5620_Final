import requests

def test_create_case():
    url = "http://localhost:8000/cases"
    files = {
        'receipt_files': ('scanned-receipt-example.webp', open('scanned-receipt-example.webp', 'rb')),
    }
    data = {
        'issue_description': 'The laptop I received is not working properly. It keeps shutting down randomly after 10 minutes of use.'
    }
    response = requests.post(url, files=files, data=data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    return response.json()

def test_analyze_case(case_id):
    url = f"http://localhost:8000/analyze?case_id={case_id}"
    response = requests.post(url)
    print("\nAnalyzing case:")
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    return response.json()

def test_classify_issue(description, case_id=None):
    url = "http://localhost:8000/classify"
    data = {
        "description": description,
        "case_id": case_id
    }
    response = requests.post(url, json=data)
    print("\nClassifying issue:")
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    return response.json()

if __name__ == "__main__":
    print("\nCreating case:")
    case = test_create_case()
    case_id = case['case_id']
    
    # Test analyze endpoint
    analysis = test_analyze_case(case_id)
    
    # Test classify endpoint
    classification = test_classify_issue(
        "The laptop I received is not working properly. It keeps shutting down randomly after 10 minutes of use.",
        case_id
    )