from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

FHIR_SERVER = "http://fhir:8080/fhir"

@app.route("/hsb/message", methods=["POST"])
def receive_message():
    bundle = request.json

    # POST al base URL si es transaction o batch
    if bundle.get("type") in ["transaction", "batch"]:
        url = FHIR_SERVER
    else:
        url = f"{FHIR_SERVER}/Bundle"

    fhir_response = requests.post(
        url,
        json=bundle,
        headers={"Content-Type": "application/fhir+json"}
    )

    return jsonify({
        "status": "forwarded to FHIR",
        "fhir_status": fhir_response.status_code,
        "fhir_response": fhir_response.json()
    }), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
