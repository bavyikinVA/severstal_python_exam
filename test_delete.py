import urllib.request

# test delete
url = 'http://127.0.0.1:7007/api/coil/8'
request = urllib.request.Request(url, method='DELETE')
response = urllib.request.urlopen(request)
print(response.read().decode())
