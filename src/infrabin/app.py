from __future__ import print_function

import os
import requests
import netifaces
import dns.resolver
import time
from flask import Flask, jsonify, request
from flask_caching import Cache
from infrabin.helpers import status_code, gzipped


app = Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE": "simple"})

liveness_healthy = True
readiness_healthy = True
AWS_METADATA_ENDPOINT = "http://169.254.169.254/latest/meta-data/"
ALL_METHODS = ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]


@app.route("/")
def main():
    return jsonify({"message": "infrabin is running"})


@app.route("/headers")
def headers():
    data = dict()
    data["method"] = request.method
    data["headers"] = dict(request.headers)
    data["origin"] = request.remote_addr
    return jsonify(data)


@app.route("/networks")
@app.route("/network/<interface>")
def network(interface=None):
    if interface:
        try:
            netifaces.ifaddresses(interface)
            interfaces = [interface]
        except ValueError:
            return jsonify({"message": "interface {} not available".format(interface)}), 404
    else:
        interfaces = netifaces.interfaces()

    data = dict()
    for i in interfaces:
        try:
            data[i] = netifaces.ifaddresses(i)[2]
        except KeyError:
            data[i] = {"message": "AF_INET data missing"}
    return jsonify(data)


@app.route("/healthcheck/liveness")
def healthcheck_liveness():
    global liveness_healthy
    if liveness_healthy:
        return jsonify({"message": "liveness probe healthy"})
    else:
        return status_code(503)


@app.route("/healthcheck/liveness/pass", methods=["POST"])
def healthcheck_liveness_pass():
    global liveness_healthy
    liveness_healthy = True
    return status_code(204)


@app.route("/healthcheck/liveness/fail", methods=["POST"])
def healthcheck_liveness_fail():
    global liveness_healthy
    liveness_healthy = False
    return status_code(204)


@app.route("/healthcheck/readiness")
def healthcheck_readiness():
    global readiness_healthy
    if readiness_healthy:
        return jsonify({"message": "readiness probe healthy"})
    else:
        return status_code(503)


@app.route("/healthcheck/readiness/pass", methods=["POST"])
def healthcheck_readiness_pass():
    global readiness_healthy
    readiness_healthy = True
    return status_code(204)


@app.route("/healthcheck/readiness/fail", methods=["POST"])
def healthcheck_readiness_fail():
    global readiness_healthy
    readiness_healthy = False
    return status_code(204)


@app.route("/env/<env_var>")
def env(env_var):
    value = os.getenv(env_var)
    if value is None:
        return status_code(404)
    else:
        return jsonify({env_var: value})


@app.route("/aws/<path:metadata_categories>")
@cache.memoize(timeout=60)
def aws(metadata_categories):
    try:
        r = requests.get(AWS_METADATA_ENDPOINT + metadata_categories, timeout=3)
    except requests.exceptions.ConnectionError:
        return jsonify({"message": "aws metadata endpoint not available"}), 501
    if r.status_code == 404:
        return status_code(404)
    return jsonify({metadata_categories: r.text})


@app.route("/status", methods=["GET", "POST"])
def status():
    response = dict()
    data = request.get_json() or {}
    # Test DNS
    nameservers = data.get("nameservers", ["8.8.8.8", "8.8.4.4"])
    if not isinstance(nameservers, list):
        return status_code(400)
    query = data.get("query", "google.com")
    resolver = dns.resolver.Resolver()
    resolver.nameservers = nameservers
    try:
        resolver.query(query)
        response["dns"] = {
            "status": "ok"
        }
    except dns.exception.DNSException as e:
        response["dns"] = {
            "status": "error",
            "reason": e.__class__.__name__
        }
    # Test external connectivity
    egress_url = data.get("egress_url", "https://www.google.com")
    try:
        requests.get(egress_url, timeout=3)
        response["egress"] = {
            "status": "ok"
        }
    except requests.exceptions.RequestException as e:
        response["egress"] = {
            "status": "error",
            "reason": e.__class__.__name__
        }
    return jsonify(response)


@app.route("/gzip")
@gzipped
def gzip():
    response = {
        "message": "this is gzip compressed"
    }
    return jsonify(response)


@app.route("/replay", methods=ALL_METHODS)
@app.route("/replay/<path:anything>", methods=ALL_METHODS)
def replay(anything=None):
    response = {
        "method": request.method
    }
    if anything:
        response["replay"] = anything
    return jsonify(response)


@app.route("/proxy", methods=["POST"])
def proxy():
    data = request.get_json()
    if not data or not isinstance(data, list):
        return status_code(400)

    response = dict()
    for e in data:
        method = e.get("method", "GET")
        payload = e.get("payload", None)
        url = e.get("url", None)
        if url:
            try:
                r = requests.request(method=method.upper(), url=url, data=payload, timeout=5)
                response[url] = {
                    "status": "ok",
                    "status_code": r.status_code,
                    # r.headers is of type requests.structures.CaseInsensitiveDict
                    # We want to convert it to a dictionary to return it into the response
                    "headers": dict(**r.headers)
                }
            except requests.exceptions.RequestException as e:
                response[url] = {
                    "status": "error",
                    # Print the class exception name that should be self explanatory
                    "reason": e.__class__.__name__
                }
        else:
            return jsonify({"message": "url missing"}), 400
    return jsonify(response)


@app.route("/delay/<int:sec>")
def delay(sec):
    time.sleep(min(sec, 120))
    return status_code(200)
