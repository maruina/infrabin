from __future__ import print_function

import os
import requests
from flask import Flask, jsonify, request
from flask.ext.cache import Cache
from .helpers import status_code


app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

is_healthy = True
AWS_METADATA_ENDPOINT = "http://169.254.169.254/latest/meta-data/"


@app.route("/")
def main():
    return jsonify({"message": "infrabin is running"})


@app.route("/headers")
def headers():
    request_data = {}
    request_data['method'] = request.method
    request_data['headers'] = dict(request.headers)
    request_data['origin'] = request.remote_addr
    return jsonify(request_data)


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
