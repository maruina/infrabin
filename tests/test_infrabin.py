from __future__ import print_function

import json
import contextlib
import os
import gzip
import time
import pytest
import socket
import infrabin.app

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


@pytest.fixture(params=infrabin.app.ALL_METHODS)
def method(request):
    return request.param


def test_main(client):
    response = client.get("/")
    data = json.loads(response.data.decode("utf-8"))
    hostname = socket.gethostname()
    assert response.status_code == 200
    assert data["message"] == "infrabin is running"
    assert data["hostname"] == hostname


def test_healthcheck_liveness_pass(client):
    response = client.get("/healthcheck/liveness")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert data == {"message": "liveness probe healthy"}


def test_healthcheck_liveness_fail(client):
    post = client.post("/healthcheck/liveness/fail")
    assert post.status_code == 204
    get = client.get("/healthcheck/liveness")
    assert get.status_code == 503


def test_healthcheck_liveness_switch(client):
    post_fail = client.post("/healthcheck/liveness/fail")
    assert post_fail.status_code == 204
    get_fail = client.get("/healthcheck/liveness")
    assert get_fail.status_code == 503
    post_pass = client.post("/healthcheck/liveness/pass")
    assert post_pass.status_code == 204
    get_pass = client.get("/healthcheck/liveness")
    get_pass_data = json.loads(get_pass.data.decode("utf-8"))
    assert get_pass.status_code == 200
    assert get_pass_data == {"message": "liveness probe healthy"}


def test_healthcheck_readiness_pass(client):
    response = client.get("/healthcheck/readiness")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert data == {"message": "readiness probe healthy"}


def test_healthcheck_readiness_fail(client):
    post = client.post("/healthcheck/readiness/fail")
    assert post.status_code == 204
    get = client.get("/healthcheck/readiness")
    assert get.status_code == 503


def test_healthcheck_readiness_switch(client):
    post_fail = client.post("/healthcheck/readiness/fail")
    assert post_fail.status_code == 204
    get_fail = client.get("/healthcheck/readiness")
    assert get_fail.status_code == 503
    post_pass = client.post("/healthcheck/readiness/pass")
    assert post_pass.status_code == 204
    get_pass = client.get("/healthcheck/readiness")
    get_pass_data = json.loads(get_pass.data.decode("utf-8"))
    assert get_pass.status_code == 200
    assert get_pass_data == {"message": "readiness probe healthy"}


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
    assert data["headers"]["User-Agent"] == "werkzeug/0.13"
    assert data["headers"]["Host"] == "localhost"


def test_networks(client):
    response = client.get("/networks")
    assert response.status_code == 200


def test_network_missing(client):
    response = client.get("/network/eth12345")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 404
    assert data == {"message": "interface eth12345 not available"}


def test_connectivity(client):
    response = client.get("/connectivity")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert data["dns"]["status"] == "ok"
    assert data["egress"]["status"] == "ok"


def test_connectivity_custom(client):
    # TODO: fix test mocking opendns and facebook.com to remove external dependencies
    payload = {
        "nameservers": [
            "208.67.222.222"
        ],
        "query": "facebook.com",
        "egress_url": "https://www.facebook.com"
    }
    response = client.post("/connectivity",
                           data=json.dumps(payload),
                           content_type='application/json')
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


def test_replay(client, method):
    response = client.open(path="/replay", method=method)
    print("Testing method {}".format(method))
    assert response.status_code == 200
    if method is not "HEAD":
        data = json.loads(response.data.decode("utf-8"))
        assert data["method"] == method


def test_replay_anything(client, method):
    response = client.open(path="/replay/meaning/of/life/42", method=method)
    print("Testing method {}".format(method))
    assert response.status_code == 200
    if method is not "HEAD":
        data = json.loads(response.data.decode("utf-8"))
        assert data["replay"] == "meaning/of/life/42"
        assert data["method"] == method


def test_proxy(client):
    payload = [
        {
            "url": "https://www.google.com"
        },
        {
            "url": "http://httpbin.org/post",
            "method": "POST",
            "payload": {
                "key": "42"
            }
        }
    ]
    response = client.post("/proxy", data=json.dumps(payload), content_type='application/json')
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert data["https://www.google.com"]["status"] == "ok"
    assert data["http://httpbin.org/post"]["status"] == "ok"


def test_proxy_bad_url(client):
    p1 = [
        {
            "url": "www.google.com"
        }
    ]
    r1 = client.post("/proxy", data=json.dumps(p1), content_type='application/json')
    d1 = json.loads(r1.data.decode("utf-8"))
    assert d1["www.google.com"]["status"] == "error"
    assert d1["www.google.com"]["reason"] == "MissingSchema"
    p2 = [
        {
            "url": "https://www.ggooggllee.comm"
        }
    ]
    r2 = client.post("/proxy", data=json.dumps(p2), content_type='application/json')
    d2 = json.loads(r2.data.decode("utf-8"))
    assert d2["https://www.ggooggllee.comm"]["status"] == "error"


def test_proxy_bad_request(client):
    p1 = {
        "key1": "value1"
    }
    r1 = client.post("/proxy", data=json.dumps(p1), content_type='application/json')
    assert r1.status_code == 400
    p2 = [
        {}
    ]
    r2 = client.post("/proxy", data=json.dumps(p2), content_type='application/json')
    data = json.loads(r2.data.decode("utf-8"))
    assert r2.status_code == 400
    assert data == {"message": "url missing"}


def test_delay(client):
    start = time.time()
    response = client.get("/delay/1")
    end = time.time()
    assert int(end - start) == 1
    assert response.status_code == 200


def test_delay_max(client):
    infrabin.app.max_delay = 2
    start = time.time()
    response = client.get("/delay/3")
    end = time.time()
    assert int(end - start) == 2
    assert response.status_code == 200


def test_status(client):
    response = client.get("/status/200")
    assert response.status_code == 200


def test_retry(client):
    # Default three 503, one 200
    response = client.get("/retry")
    assert response.status_code == 503
    response = client.get("/retry")
    assert response.status_code == 503
    response = client.get("/retry")
    assert response.status_code == 503
    response = client.get("/retry")
    assert response.status_code == 200


def test_retry_custom(client):
    infrabin.app.max_retries = 2
    response = client.get("/retry")
    assert response.status_code == 503
    response = client.get("/retry")
    assert response.status_code == 503
    response = client.get("/retry")
    assert response.status_code == 200

    infrabin.app.max_retries = 0
    response = client.get("/retry")
    assert response.status_code == 200


def test_retry_status(client):
    infrabin.app.max_retries = 2
    response = client.get("/retry/max_retries")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert data["max_retries"] == 2


def test_bytes(client):
    size = 15
    response = client.get("/bytes/{}".format(size))
    assert response.status_code == 200
    assert response.headers["Content-Length"] == str(size)


def test_bytes_max(client):
    infrabin.app.max_size = 64
    size = 128
    response = client.get("/bytes/{}".format(size))
    assert response.status_code == 200
    assert response.headers["Content-Length"] == str(infrabin.app.max_size)
