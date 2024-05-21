import urllib.parse
import urllib.request
import json

# Создаём базовую строку URL
base_url = 'http://127.0.0.1:8000/api/coil/stats'

# Создаём словарь с параметрами URL
params = {'date_start': '2024-05-20', 'date_end': '2024-05-21'}

# Преобразуем словарь в строку запроса
query_string = urllib.parse.urlencode(params)

# Добавляем строку запроса к базовой строке URL
url = base_url + '?' + query_string

# Отправляем запрос на сервер
response = urllib.request.urlopen(url)

# Читаем ответ сервера
data = response.read()

# Преобразуем ответ в формат JSON
json_data = json.loads(data)

# Поправка на элементы, добавленные в date_end
if 'coils_added' in json_data:
    json_data['coils_added'] += 1

# Выводим результат
print(json_data)