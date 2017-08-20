from __future__ import print_function

import json
import contextlib
import os
import gzip
from io import BytesIO


@contextlib.contextmanager
def _setenv(key, value):
    """Context manager to set an environment variable temporarily."""
    old_value = os.environ.get(key, None)
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value

    yield

    if old_value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value


def test_main(client):
    response = client.get("/")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert data == {"message": "infrabin is running"}


def test_healthcheck_pass(client):
    response = client.get("/healthcheck")
    data = json.loads(response.data.decode("utf-8"))
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
    get_pass_data = json.loads(get_pass.data.decode("utf-8"))
    assert get_pass.status_code == 200
    assert get_pass_data == {"message": "infrabin is healthy"}


def test_env_if_present(client):
    with _setenv("VERSION", "v1"):
        response = client.get("/env/VERSION")
        data = json.loads(response.data.decode("utf-8"))
        assert response.status_code == 200
        assert data == {"VERSION": "v1"}


def test_env_if_missing(client):
    response = client.get("/env/VERSION")
    assert response.status_code == 404


def test_aws(client):
    # TODO: find a good way to test this function
    pass


def test_headers(client):
    response = client.get("/headers", headers={"X-Meaning-Of-Life": "42"})
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert data["method"] == "GET"
    assert data["origin"] == "127.0.0.1"
    assert data["headers"]["X-Meaning-Of-Life"] == "42"
    assert data["headers"]["User-Agent"] == "werkzeug/0.12.2"
    assert data["headers"]["Host"] == "localhost"


def test_networks(client):
    response = client.get("/networks")
    assert response.status_code == 200


def test_network_missing(client):
    response = client.get("/network/eth12345")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 404
    assert data == {"message": "interface eth12345 not available"}


def test_status(client):
    response = client.get("/status")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert data["dns"]["status"] == "ok"
    assert data["egress"]["status"] == "ok"


def test_status_custom(client):
    # TODO: fix test mocking opendns and facebook.com to remove external dependencies
    payload = {
        "nameservers": [
            "208.67.222.222"
        ],
        "query": "facebook.com",
        "egress_url": "https://www.facebook.com"
    }
    response = client.post("/status", data=json.dumps(payload), content_type='application/json')
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert data["dns"]["status"] == "ok"
    assert data["egress"]["status"] == "ok"


def test_gzip(client):
    response = client.get("/gzip")
    buffer = BytesIO(response.data)
    encoded_message = gzip.GzipFile(mode='rb', fileobj=buffer).read()
    data = json.loads(encoded_message.decode("utf-8"))
    assert response.status_code == 200
    assert response.headers["Content-Encoding"] == "gzip"
    assert data == {"message": "this is gzip compressed"}


def test_replay(client):
    response = client.get("/replay/meaning/of/life/42")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert data["replay"] == "meaning/of/life/42"
