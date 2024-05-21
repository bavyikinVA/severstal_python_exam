import urllib.request
import json

url = 'http://127.0.0.1:8000/api/coil'
headers = {'Content-Type': 'application/json'}
data = {'length': 1000, 'weight': 100000}
data_json = json.dumps(data)
data_bytes = data_json.encode('utf-8')
request = urllib.request.Request(url, data=data_bytes, headers=headers)
response = urllib.request.urlopen(request)
print(response.read().decode())
