from __future__ import print_function

import os
import requests
import netifaces
import dns.resolver
from flask import Flask, jsonify, request
from flask_cache import Cache
from infrabin.helpers import status_code


app = Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE": "simple"})

is_healthy = True
AWS_METADATA_ENDPOINT = "http://169.254.169.254/latest/meta-data/"


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


@app.route("/healthcheck")
def healthcheck():
    global is_healthy
    if is_healthy:
        return jsonify({"message": "infrabin is healthy"})
    else:
        return status_code(503)


@app.route("/healthcheck/pass", methods=["POST"])
def healthcheck_pass():
    global is_healthy
    is_healthy = True
    return status_code(204)


@app.route("/healthcheck/fail", methods=["POST"])
def healthcheck_fail():
    global is_healthy
    is_healthy = False
    return status_code(204)


@app.route("/env/<env_var>")
def env(env_var):
    value = os.getenv(env_var)
    if value is None:
        return status_code(404)
    else:
        return jsonify({env_var: value})


@cache.memoize()
@app.route("/aws/<metadata_categories>")
def aws(metadata_categories):
    try:
        r = requests.get(AWS_METADATA_ENDPOINT + metadata_categories, timeout=1)
    except requests.exceptions.ConnectionError:
        return jsonify({"message": "aws metadata endpoint not available"}), 501
    if r.status_code == 404:
        return status_code(404)
    return jsonify({metadata_categories: r})


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
