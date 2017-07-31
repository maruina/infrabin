from __future__ import print_function

import json


def test_main(client):
    response = client.get("/")
    data = json.loads(response.data.decode('utf-8'))
    assert response.status_code == 200
    assert data == {"msg": "infrabin is running"}
