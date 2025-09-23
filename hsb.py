from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)
HAPI_URL = "http://hapi-fhir:8080/fhir"  # usa el nombre del contenedor HAPI

@app.route("/hsb", methods=["POST"])
def hsb():
    bundle = request.get_json()
    for entry in bundle.get("entry", []):
        resource = entry.get("resource")
        if resource:
            r_type = resource["resourceType"]
            r_id = resource.get("id")
            success = False
            for _ in range(5):  # reintentos en caso de que HAPI no esté listo
                try:
                    r = requests.put(f"{HAPI_URL}/{r_type}/{r_id}", json=resource)
                    if r.status_code in (200, 201):
                        success = True
                        break
                except requests.exceptions.RequestException:
                    time.sleep(2)
            if not success:
                print(f"Error enviando {r_type}/{r_id}")
    return jsonify({"status": "Bundle enviado a HAPI"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
