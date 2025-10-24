"""
backend.smoke_receipt_id

Smoke test for /cases and /analyze using a provided receipt_id (no database needed).
This validates that:
 - /cases accepts receipt_id via Form, stores it, and echoes it in response
 - /analyze with the returned case_id runs and returns status/timestamps/progress
"""

from fastapi.testclient import TestClient
from backend.main import app


def main():
    client = TestClient(app)

    fake_receipt_id = "RCP-TEST-0001"

    # Create case with receipt_id and issue_description (no files, no DB)
    r = client.post('/cases', data={
        'receipt_id': fake_receipt_id,
        'issue_description': 'Test: The received product is damaged and needs return/exchange/claim.',
    })
    print('POST /cases', r.status_code)
    data = r.json()
    print('cases json:', data)

    assert r.status_code == 200, '/cases should return 200'
    assert 'case_id' in data, 'response should contain case_id'
    assert data.get('receipt_id') == fake_receipt_id, 'response should echo provided receipt_id'
    assert data.get('status') == 'case_created', 'status should be case_created initially'

    case_id = data['case_id']

    # Analyze with case_id to get status/timestamps/progress in response
    r2 = client.post('/analyze', data={
        'issue_description': 'Outer package is damaged and internal accessories are missing.',
        'case_id': case_id,
    })
    print('POST /analyze', r2.status_code)
    data2 = r2.json()
    print('analyze json:', data2)

    assert r2.status_code == 200, '/analyze should return 200'
    assert data2.get('status') in ['analysis_completed', 'analysis_failed'], 'status should be final'
    assert isinstance(data2.get('progress_percent'), int), 'progress_percent should be int'
    assert 'timestamps' in data2, 'timestamps should be present'


if __name__ == '__main__':
    main()
