"""
backend.smoke_status

Smoke test for /cases and /analyze with status integration.
"""

from fastapi.testclient import TestClient
from backend.main import app


def main():
    client = TestClient(app)

    r = client.post('/cases', data={'issue_description': 'test issue'})
    print('POST /cases', r.status_code)
    data = r.json()
    print('cases json:', data)
    case_id = data.get('case_id')

    r2 = client.post('/analyze', data={'issue_description': 'Package not shipped yet', 'case_id': case_id})
    print('POST /analyze', r2.status_code)
    data2 = r2.json()
    print('analyze status:', data2.get('status'))
    print('analyze progress:', data2.get('progress_percent'))
    print('analyze timestamps:', data2.get('timestamps'))


if __name__ == '__main__':
    main()
