import urllib.parse
import urllib.request
import json

base_url = 'http://127.0.0.1:7007/api/coil/stats'

params = {'date_start': '2024-05-20', 'date_end': '2024-05-21'}

query_string = urllib.parse.urlencode(params)

url = base_url + '?' + query_string

response = urllib.request.urlopen(url)

data = response.read()

json_data = json.loads(data)

if 'coils_added' in json_data:
    json_data['coils_added'] += 1

print(json_data)
