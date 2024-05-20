import urllib.request

# test get api coil
url = 'http://127.0.0.1:8000/api/coil?id_min=3&id_max=5'
headers = {'Content-Type': 'application/json'}
request = urllib.request.Request(url, headers=headers)
response = urllib.request.urlopen(request)
print(response.read().decode())
