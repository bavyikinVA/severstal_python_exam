import urllib.request

# test delete
url = 'http://127.0.0.1:8000/api/coil/7'
request = urllib.request.Request(url, method='DELETE')
response = urllib.request.urlopen(request)
print(response.read().decode())
