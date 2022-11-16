from flask import Flask, jsonify
from flask_cors import CORS,cross_origin

app = Flask(__name__)
CORS(app)
@cross_origin
@app.route("/")
def hello_world():
    return jsonify({"title":"prueba",
                    "version":"v0.0.1"})

from app.routes.route import lectura_bp
app.register_blueprint(lectura_bp)

if __name__ == "__main__":
    app.run(
        port=5000,
        debug=True,
        host="0.0.0.0"
    )