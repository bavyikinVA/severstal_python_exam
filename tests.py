import urllib.request
import json
from utils import config_parser
import urllib.parse

config = config_parser('config.txt')
BASE_URL = f"http://{config['SERVER_HOST']}:{config['SERVER_PORT']}"


def test_main_route():
    with urllib.request.urlopen(f"{BASE_URL}/") as response:
        assert response.status == 200


def test_create_coil():
    coil_data = {"length": 15, "weight": 50.0}
    data = json.dumps(coil_data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    request = urllib.request.Request(f"{BASE_URL}/api/coil", data=data, headers=headers)
    with urllib.request.urlopen(request) as response:
        assert response.status == 200
        coil_id = response.read().decode("utf-8")
        return coil_id


def test_delete_coil():
    coil_id = test_create_coil()

    url = f"{BASE_URL}/api/coil/{coil_id}"
    encoded_url = urllib.parse.quote(url, safe=':/')

    request = urllib.request.Request(encoded_url, method='DELETE')
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e}")


def test_get_coils_by_id():
    base_url = f"{BASE_URL}/api/coil/"
    filters = {'id_min': 5, 'id_max': 10}

    url = f"{base_url}?{urllib.parse.urlencode(filters)}"
    headers = {'Content-Type': 'application/json'}

    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)
    assert response.getcode() == 200


def test_get_coils_by_weight():
    base_url = f"{BASE_URL}/api/coil/"
    filters = {'weight_min': 5, 'weight_max': 200}  # Фильтр по весу

    url = f"{base_url}?{urllib.parse.urlencode(filters)}"
    headers = {'Content-Type': 'application/json'}

    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)
    assert response.getcode() == 200


def test_get_coils_with_multiple_params():
    base_url = f"{BASE_URL}/api/coil/"
    filters = {
        'weight_min': 6,
        'weight_max': 60,
        'length_min': 5,
        'length_max': 20,
        'created_after': '2024-05-21',
        'deleted_before': '2024-01-22'
    }

    url = f"{base_url}?{urllib.parse.urlencode(filters)}"
    headers = {'Content-Type': 'application/json'}

    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)

    assert response.getcode() == 200


def test_get_stats():
    base_url = f"{BASE_URL}/api/coil/stats"

    params = {'date_start': '2024-05-20', 'date_end': '2024-05-21'}

    query_string = urllib.parse.urlencode(params)

    url = base_url + '?' + query_string

    response = urllib.request.urlopen(url)

    data = response.read()

    json_data = json.loads(data)

    if 'coils_added' in json_data:
        json_data['coils_added'] += 1

    assert response.getcode() == 200
