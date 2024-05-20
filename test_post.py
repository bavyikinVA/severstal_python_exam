import urllib.request
import json

url = 'http://127.0.0.1:8000/api/coil'
headers = {'Content-Type': 'application/json'}
data = {'length': 1.25, 'weight': 6.56}
data_json = json.dumps(data)  # преобразование в JSON-строку
data_bytes = data_json.encode('utf-8')  # преобразование в bytes
request = urllib.request.Request(url, data=data_bytes, headers=headers)
response = urllib.request.urlopen(request)
print(response.read().decode())
