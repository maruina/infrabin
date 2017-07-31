from flask import Flask, jsonify

# def create_app(debug=False):
#     app = Flask(__name__)
#     app.debug = debug
#     return app
# app=create_app()

app = Flask(__name__)

@app.route("/")
def main():
    return jsonify({"msg": "infrabin is running"})




if __name__ == "__main__":
    app = create_app()
    app.run()