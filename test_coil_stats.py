import urllib.request

url = 'http://0.0.0.0:8000/api/coil/stats?start_date=2022-01-01&end_date=2022-02-01'
response = urllib.request.urlopen(url)
print(response.read().decode())
