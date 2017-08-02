from flask import Flask, jsonify
from .helpers import status_code


app = Flask(__name__)
is_healthy = True


@app.route("/")
def main():
    return jsonify({"message": "infrabin is running"})


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
