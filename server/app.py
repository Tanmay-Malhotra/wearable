from flask import Flask, request, jsonify
from flask_cors import CORS
from power_manager import manage_battery_api

app = Flask(__name__)
CORS(app)  # allow frontend to call backend
@app.route("/", methods=["GET"])
def index():
    return "Battery Management API is running."

@app.route("/manage-battery", methods=["POST"])
def manage_battery_route():
    data = request.json
    result = manage_battery_api(data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)
