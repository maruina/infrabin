from __future__ import print_function

import json


def test_main(client):
    response = client.get("/")
    json_data = json.loads(response.get_data())
    assert response.status_code == 200
    assert json_data == {"msg": "infrabin is running"}