from __future__ import print_function

import os
import requests
import netifaces
import dns.resolver
import time
import socket
from random import randint
from flask import Flask, jsonify, request, make_response
from flask_caching import Cache
from infrabin.helpers import status_code, gzipped, fib
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import Counter, make_wsgi_app


app = Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE": "simple"})
# Add prometheus wsgi middleware to route /metrics requests
app_dispatch = DispatcherMiddleware(app, {"/metrics": make_wsgi_app()})
c = Counter(
    "infrabin_http_requests_total",
    "total number of requests",
    ["method", "endpoint", "code"],
)


AWS_METADATA_ENDPOINT = "http://169.254.169.254/latest/meta-data/"
ALL_METHODS = [
    "GET",
    "HEAD",
    "POST",
    "PUT",
    "DELETE",
    "CONNECT",
    "OPTIONS",
    "TRACE",
    "PATCH",
]
LOG_LEVELS = {"CRITICAL": 50, "ERROR": 40, "WARNING": 30, "INFO": 20, "DEBUG": 10}
liveness_healthy = True
readiness_healthy = True
retries = 0
max_retries = int(os.getenv("MAX_RETRIES", 3))
max_delay = int(os.getenv("MAX_DELAY", 120))
max_size = int(os.getenv("MAX_SIZE", 1024 * 1024))  # Max 1Mb


@app.route("/")
def main():
    data = dict()
    data["hostname"] = socket.gethostname()
    data["message"] = "infrabin is running"
    c.labels(request.method, request.path, 200).inc()
    return jsonify(data)


@app.route("/headers")
def headers():
    data = dict()
    data["method"] = request.method
    data["headers"] = dict(request.headers)
    data["origin"] = request.remote_addr
    c.labels(request.method, request.path, 200).inc()
    return jsonify(data)


@app.route("/networks")
@app.route("/network/<interface>")
def network(interface=None):
    if interface:
        try:
            netifaces.ifaddresses(interface)
            interfaces = [interface]
        except ValueError:
            c.labels(request.method, request.path, 404).inc()
            return (
                jsonify({"message": "interface {} not available".format(interface)}),
                404,
            )
    else:
        interfaces = netifaces.interfaces()
    data = dict()
    for i in interfaces:
        try:
            data[i] = netifaces.ifaddresses(i)[2]
        except KeyError:
            data[i] = {"message": "AF_INET data missing"}
    c.labels(request.method, request.path, 200).inc()
    return jsonify(data)


@app.route("/healthcheck/liveness")
def healthcheck_liveness():
    global liveness_healthy
    if liveness_healthy:
        c.labels(request.method, request.path, 200).inc()
        return jsonify({"message": "liveness probe healthy"})
    else:
        c.labels(request.method, request.path, 503).inc()
        return status_code(503)


@app.route("/healthcheck/liveness/pass", methods=["POST"])
def healthcheck_liveness_pass():
    global liveness_healthy
    liveness_healthy = True
    c.labels(request.method, request.path, 204).inc()
    return status_code(204)


@app.route("/healthcheck/liveness/fail", methods=["POST"])
def healthcheck_liveness_fail():
    global liveness_healthy
    liveness_healthy = False
    c.labels(request.method, request.path, 204).inc()
    return status_code(204)


@app.route("/healthcheck/readiness")
def healthcheck_readiness():
    global readiness_healthy
    if readiness_healthy:
        c.labels(request.method, request.path, 200).inc()
        return jsonify({"message": "readiness probe healthy"})
    else:
        c.labels(request.method, request.path, 503).inc()
        return status_code(503)


@app.route("/healthcheck/readiness/pass", methods=["POST"])
def healthcheck_readiness_pass():
    global readiness_healthy
    readiness_healthy = True
    c.labels(request.method, request.path, 204).inc()
    return status_code(204)


@app.route("/healthcheck/readiness/fail", methods=["POST"])
def healthcheck_readiness_fail():
    global readiness_healthy
    readiness_healthy = False
    c.labels(request.method, request.path, 204).inc()
    return status_code(204)


@app.route("/env/<env_var>")
def env(env_var):
    value = os.getenv(env_var)
    if value is None:
        c.labels(request.method, request.path, 404).inc()
        return status_code(404)
    else:
        c.labels(request.method, request.path, 200).inc()
        return jsonify({env_var: value})


@app.route("/aws/<path:metadata_category>")
@cache.memoize(timeout=60)
def aws(metadata_category):
    try:
        r = requests.get(AWS_METADATA_ENDPOINT + metadata_category, timeout=3)
    except requests.exceptions.RequestException as e:
        c.labels(request.method, request.path, 502).inc()
        return (
            jsonify(
                {
                    "message": "aws metadata endpoint not available",
                    "reason": e.__class__.__name__,
                }
            ),
            502,
        )
    if r.status_code == 404:
        c.labels(request.method, request.path, 404).inc()
        return status_code(404)
    c.labels(request.method, request.path, 202).inc()
    return jsonify({metadata_category: r.text})


@app.route("/connectivity", methods=["GET", "POST"])
def connectivity():
    response = dict()
    data = request.get_json() or {}
    # Test DNS
    nameservers = data.get("nameservers", ["8.8.8.8", "8.8.4.4"])
    if not isinstance(nameservers, list):
        c.labels(request.method, request.path, 404).inc()
        return status_code(400)
    query = data.get("query", "google.com")
    resolver = dns.resolver.Resolver()
    resolver.nameservers = nameservers
    try:
        resolver.query(query)
        response["dns"] = {"status": "ok"}
    except dns.exception.DNSException as e:
        response["dns"] = {"status": "error", "reason": e.__class__.__name__}
    # Test external connectivity
    egress_url = data.get("egress_url", "https://www.google.com")
    try:
        requests.get(egress_url, timeout=3)
        response["egress"] = {"status": "ok"}
    except requests.exceptions.RequestException as e:
        response["egress"] = {"status": "error", "reason": e.__class__.__name__}
    c.labels(request.method, request.path, 200).inc()
    return jsonify(response)


@app.route("/gzip")
@gzipped
def gzip():
    response = {"message": "this is gzip compressed"}
    c.labels(request.method, request.path, 200).inc()
    return jsonify(response)


@app.route("/proxy", methods=["POST"])
def proxy():
    data = request.get_json()
    if not data or not isinstance(data, list):
        c.labels(request.method, request.path, 400).inc()
        return status_code(400)

    http_proxy = os.getenv("http_proxy", None)
    if http_proxy:
        proxies = {
            "http": "http://{}".format(http_proxy),
            "https": "http://{}".format(http_proxy),
        }
    else:
        proxies = None

    response = dict()
    for e in data:
        method = e.get("method", "GET")
        payload = e.get("payload", None)
        url = e.get("url", None)
        if url:
            try:
                r = requests.request(
                    method=method.upper(),
                    url=url,
                    data=payload,
                    timeout=5,
                    proxies=proxies,
                )
                response[url] = {
                    "status": "ok",
                    "status_code": r.status_code,
                    # r.headers is of type requests.structures.CaseInsensitiveDict
                    # We want to convert it to a dictionary
                    # to return it into the response
                    "headers": dict(**r.headers),
                }
            except requests.exceptions.RequestException as e:
                response[url] = {
                    "status": "error",
                    # Print the class exception name that should be self explanatory
                    "reason": e.__class__.__name__,
                }
        else:
            c.labels(request.method, request.path, 400).inc()
            return jsonify({"message": "url missing"}), 400
    c.labels(request.method, request.path, 200).inc()
    return jsonify(response)


@app.route("/delay/<int:sec>")
def delay(sec):
    global max_delay
    time.sleep(min(sec, max_delay))
    c.labels(request.method, request.path, 200).inc()
    return status_code(200)


@app.route("/status/<int:code>")
def status(code):
    c.labels(request.method, request.path, code).inc()
    return status_code(code)


@app.route("/retry")
def retry():
    global retries
    global max_retries

    if retries < max_retries:
        retries += 1
        c.labels(request.method, request.path, 503).inc()
        return status_code(503)
    else:
        retries = 0
        c.labels(request.method, request.path, 200).inc()
        return status_code(200)


@app.route("/retry/max_retries")
def max_retries_status():
    global max_retries
    c.labels(request.method, request.path, 200).inc()
    return jsonify({"max_retries": max_retries}), 200


@app.route("/bytes/<int:n>", methods=["GET", "POST"])
def bytes(n):
    global max_size
    n = min(n, max_size)
    response = make_response()
    response.data = bytearray(randint(0, 255) for i in range(n))
    response.content_type = "application/octet-stream"
    response.status_code = 200
    c.labels(request.method, request.path, 200).inc()
    return response


@app.route("/mirror", methods=ALL_METHODS)
def mirror():
    response = make_response()
    response.data = request.get_data()
    response.headers = request.headers
    c.labels(request.method, request.path, 200).inc()
    return response


@app.route("/fibonacci/<int:n>", methods=["GET"])
def fibonacci(n):
    result = fib(n)
    response = {"response": result}
    c.labels(request.method, request.path, 200).inc()
    return jsonify(response)


@app.route("/log", methods=["POST"])
def record_log():
    data = request.get_json() or {}
    severity = data.get("severity", "INFO")
    message = data.get("message", "")
    if all([data, severity, message]) and severity in LOG_LEVELS:
        app.logger.log(LOG_LEVELS[severity], message)
        c.labels(request.method, request.path, 200).inc()
        return status_code(200)
    else:
        c.labels(request.method, request.path, 400).inc()
        return status_code(400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
