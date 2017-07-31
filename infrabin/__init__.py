from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def main():
    return jsonify({"msg": "infrabin is running!"})