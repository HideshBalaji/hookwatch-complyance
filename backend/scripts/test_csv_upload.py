import urllib.request
import urllib.parse
import os

# Configuration
URL = 'http://127.0.0.1:8000/api/v1/webhooks/upload/csv?user_id=user_1'
FILE_PATH = 'datasets/sample_upload.csv'

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
with open(FILE_PATH, 'rb') as f:
    csv_data = f.read()

# Build Multipart Form Data
body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="sample_upload.csv"\r\n'
    f'Content-Type: text/csv\r\n\r\n'
).encode('utf-8') + csv_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')

req = urllib.request.Request(
    URL,
    data=body,
    headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body))
    }
)

try:
    response = urllib.request.urlopen(req)
    print("Upload Successful!")
    print(response.read().decode())
except Exception as e:
    print("Upload Failed!")
    print(e.read().decode() if hasattr(e, 'read') else e)
