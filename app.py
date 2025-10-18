from flask import Flask, render_template, request, jsonify
from scraper import get_districts

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# --- API Endpoint ---
@app.route("/api/districts", methods=["POST"])
def districts_api():
    if not request.is_json:
        return jsonify({"error": "Invalid request, JSON expected"}), 400

    content = request.get_json()
    state_code = content.get("state_code")
    if not state_code:
        return jsonify({"error": "state_code is required"}), 400

    try:
        # print(state_code)
        districts = get_districts(state_code)
        # print(districts)
        return jsonify(districts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
