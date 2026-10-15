from flask import Flask, jsonify
import json
from pathlib import Path

app = Flask(__name__)

DATA_PATH = Path(__file__).parent / "data" / "mock_crm.json"


def load_crm_data():
    """Load CRM profiles from the local JSON file."""
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/health")
def health_check():
    return jsonify({"status": "ok"}), 200


@app.get("/clients/<client_id>")
def get_client(client_id):
    """Return a CRM profile for the requested client."""
    try:
        crm_data = load_crm_data()
    except (OSError, json.JSONDecodeError):
        app.logger.exception("Failed to load CRM data")
        return jsonify({"error": "CRM data unavailable"}), 500

    client = crm_data.get(client_id)

    if client is None:
        return jsonify({"error": "Client not found"}), 404

    return jsonify(client), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
