import urllib.request
import json

url = 'http://127.0.0.1:7007/api/coil'
headers = {'Content-Type': 'application/json'}
data = {'length': 54, 'weight': 1234}
data_json = json.dumps(data)
data_bytes = data_json.encode('utf-8')
request = urllib.request.Request(url, data=data_bytes, headers=headers)
response = urllib.request.urlopen(request)
print(response.read().decode())
