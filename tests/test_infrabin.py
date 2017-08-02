from __future__ import print_function

import json


def test_main(client):
    response = client.get("/")
    data = json.loads(response.data.decode('utf-8'))
    assert response.status_code == 200
    assert data == {"message": "infrabin is running"}


def test_healthcheck_pass(client):
    response = client.get("/healthcheck")
    data = json.loads(response.data.decode('utf-8'))
    assert response.status_code == 200
    assert data == {"message": "infrabin is healthy"}


def test_healthcheck_fail(client):
    post = client.post("/healthcheck/fail")
    assert post.status_code == 204
    get = client.get("/healthcheck")
    assert get.status_code == 503


def test_healthcheck_switch(client):
    post_fail = client.post("/healthcheck/fail")
    assert post_fail.status_code == 204
    get_fail = client.get("/healthcheck")
    assert get_fail.status_code == 503
    post_pass = client.post("/healthcheck/pass")
    assert post_pass.status_code == 204
    get_pass = client.get("/healthcheck")
    get_pass_data = json.loads(get_pass.data.decode('utf-8'))
    assert get_pass.status_code == 200
    assert get_pass_data == {"message": "infrabin is healthy"}
