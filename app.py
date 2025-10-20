from flask import Flask, render_template, request, jsonify, send_from_directory
from scraper import get_districts, get_court_complexes, get_court_establishments, get_court_names
from final_scraper import main as scrape_cause_list
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

@app.route("/api/complexes", methods=["POST"])
def complexes_api():
    if not request.is_json:
        return jsonify({"error": "Invalid request, JSON expected"}), 400

    content = request.get_json()
    state_code = content.get("state_code")
    district_code = content.get("district_code")

    if not state_code or not district_code:
        return jsonify({"error": "state_code and district_code are required"}), 400

    try:
        complexes = get_court_complexes(state_code, district_code)
        return jsonify(complexes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/establishments", methods=["POST"])
def establishments_api():
    if not request.is_json:
        return jsonify({"error": "Invalid request, JSON expected"}), 400

    content = request.get_json()
    state_code = content.get("state_code")
    dist_code = content.get("district_code")
    complex_code = content.get("complex_code")

    if not all([state_code, dist_code, complex_code]):
        return jsonify({"error": "state_code, district_code, and complex_code are required"}), 400

    try:
        establishments = get_court_establishments(state_code, dist_code, complex_code)
        return jsonify(establishments)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/court_names', methods=['POST'])
def format_cause_list_api():
    if not request.is_json:
        return jsonify({"error": "Invalid request, JSON expected"}), 400

    content = request.get_json()
    state_code = content.get("state_code")
    dist_code = content.get("district_code")
    complex_code = content.get("complex_code")
    establishment_code = content.get("establishment_code")

    if not all([state_code, dist_code, complex_code]):
        return jsonify({"error": "state_code, district_code, complex_code and establishment code are required"}), 400

    try:
        establishments = get_court_names(state_code, dist_code, complex_code, establishment_code)
        return jsonify(establishments)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download_cause_list', methods=['POST'])
def generate_cause_list():
    if not request.is_json:
        return jsonify({"error": "Invalid request, JSON expected"}), 400

    content = request.get_json()

    cl_court_no = content.get("cl_court_no")
    court_name = content.get("court_name")
    causelist_date = content.get("causelist_date")
    state_code = content.get("state_code")
    dist_code = content.get("dist_code")
    complex_code = content.get("court_complex_code")
    establishment_code = content.get("est_code")
    # cl_court_no, court_name, causelist_date, state_code, dist_code, court_complex_code, est_code
    if not all([state_code, dist_code, complex_code]):
        return jsonify({"error": "cl_court_no, court_name, causelist_date, state_code, dist_code, court_complex_code and establishment code are required"}), 400

    try:
        res = scrape_cause_list(cl_court_no, court_name, causelist_date, state_code, dist_code, complex_code, establishment_code)
        return jsonify({"is_generated": res})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_pdf')
def download_pdf():
    """Serve the generated PDF file."""
    return send_from_directory('static', 'case_data.pdf', as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)


