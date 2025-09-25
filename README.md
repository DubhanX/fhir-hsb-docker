# 🚀 FHIR + HSB Dockerizado

Este proyecto configura un **simulador HSB (Health System Broker)** en Python y un servidor **HAPI FHIR** usando Docker y Docker Compose.
Permite crear, enviar y verificar recursos FHIR (`Patient`, `Encounter`, `MessageHeader`) y bundles tipo `transaction`.

---

## 🔹 Requisitos Previos

* 🐳 **Docker**
* 🐙 **Docker Compose**
* 💻 **curl**
* 📜 **jq** (opcional, para formatear JSON)

Verifica las instalaciones:

```bash
docker --version
docker compose version
```

---

## 🔹 Paso 0: Preparativos

Crear directorio para el proyecto:

```bash
cd ~
mkdir -p fhir-hsb
cd fhir-hsb
```

---

## 🔹 Paso 1: Crear HSB (simulador) en Python

### 1️⃣1 Crear `requirements.txt`:

```bash
cat > requirements.txt << 'EOF'
flask
requests
EOF
```

### 1️⃣2 Crear `app.py`:

```bash
cat > app.py << 'EOF'
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

FHIR_SERVER = "http://fhir:8080/fhir"

@app.route("/hsb/message", methods=["POST"])
def receive_message():
    bundle = request.json
    url = FHIR_SERVER if bundle.get("type") in ["transaction", "batch"] else f"{FHIR_SERVER}/Bundle"
    fhir_response = requests.post(url, json=bundle, headers={"Content-Type": "application/fhir+json"})
    return jsonify({
        "status": "forwarded to FHIR",
        "fhir_status": fhir_response.status_code,
        "fhir_response": fhir_response.json()
    }), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
EOF
```

### 1️⃣3 Crear `Dockerfile`:

```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
EOF
```

---

## 🔹 Paso 2: Crear `docker-compose.yml`

```bash
cat > docker-compose.yml << 'EOF'
services:
  fhir:
    image: hapiproject/hapi:latest
    container_name: hapi-fhir
    ports:
      - "8080:8080"

  hsb:
    build: .
    container_name: hsb
    ports:
      - "5000:5000"
    depends_on:
      - fhir
EOF
```

---

## 🔹 Paso 3: Levantar los contenedores

```bash
docker compose up --build -d
docker ps  # Verifica que estén activos
```

* `hapi-fhir` → `localhost:8080`
* `hsb` → `localhost:5000`

Para detener y limpiar:

```bash
docker compose down
```

---

## 🔹 Paso 4: Crear recursos FHIR

### 4️⃣1 Crear paciente `p3`

```bash
cat > patient.json << 'EOF'
{
  "resourceType": "Patient",
  "id": "p3",
  "name": [ { "use": "official", "family": "Pineres", "given": ["Dubhan"] } ],
  "gender": "male",
  "birthDate": "2003-07-31"
}
EOF

curl -X PUT "http://localhost:8080/fhir/Patient/p3" -H "Content-Type: application/fhir+json" -d @patient.json
```

### 4️⃣2 Crear Encounter `e-p3`

```bash
cat > encounter.json << 'EOF'
{
  "resourceType": "Encounter",
  "id": "e-p3",
  "status": "planned",
  "subject": { "reference": "Patient/p3" }
}
EOF

curl -X PUT "http://localhost:8080/fhir/Encounter/e-p3" -H "Content-Type: application/fhir+json" -d @encounter.json
```

### 4️⃣3 Crear MessageHeader `msg-3`

```bash
cat > messageheader.json << 'EOF'
{
  "resourceType": "MessageHeader",
  "id": "msg-3",
  "eventCoding": {
    "system": "http://hl7.org/fhir/message-events",
    "code": "admin-notify"
  },
  "source": {
    "name": "HSB-Simulator",
    "endpoint": "http://localhost:5000/hsb"
  },
  "focus": [ { "reference": "Encounter/e-p3" } ]
}
EOF

curl -X PUT "http://localhost:8080/fhir/MessageHeader/msg-3" -H "Content-Type: application/fhir+json" -d @messageheader.json
```

---

## 🔹 Paso 5: Verificar recursos

```bash
curl http://localhost:8080/fhir/Patient/p3 | jq .
curl http://localhost:8080/fhir/Encounter/e-p3 | jq .
curl http://localhost:8080/fhir/MessageHeader/msg-3 | jq .
```

---

## 🔹 Paso 6: Enviar bundle tipo transaction desde HSB

```bash
cat > bundle-transaction.json << 'EOF'
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    { "resource": { "resourceType": "Patient", "id": "p3", "name":[{"use":"official","family":"Pineres","given":["Dubhan"]}], "gender":"male", "birthDate":"2003-07-31" }, "request": {"method":"PUT","url":"Patient/p3"} },
    { "resource": { "resourceType": "Encounter", "id": "e-p3", "status": "planned", "subject": {"reference": "Patient/p3"} }, "request": {"method":"PUT","url":"Encounter/e-p3"} },
    { "resource": { "resourceType": "MessageHeader", "id": "msg-3", "eventCoding": {"system":"http://hl7.org/fhir/message-events","code":"admin-notify"}, "source":{"name":"HSB-Simulator","endpoint":"http://localhost:5000/hsb"}, "focus":[{"reference":"Encounter/e-p3"}]}, "request":{"method":"PUT","url":"MessageHeader/msg-3"}}
  ]
}
EOF

curl -X POST "http://localhost:5000/hsb/message" -H "Content-Type: application/fhir+json" -d @bundle-transaction.json
```

---

## 🔹 Paso 7: Verificar recursos nuevamente

```bash
curl http://localhost:8080/fhir/Patient/p3 | jq .
curl http://localhost:8080/fhir/Encounter/e-p3 | jq .
curl http://localhost:8080/fhir/MessageHeader/msg-3 | jq .
```

---

## 🔹 Paso 8: Verificación final en Postman

1. Abrir Postman.
2. Crear requests **GET** para cada recurso:

   * `Patient`: `http://localhost:8080/fhir/Patient/p3`
   * `Encounter`: `http://localhost:8080/fhir/Encounter/e-p3`
   * `MessageHeader`: `http://localhost:8080/fhir/MessageHeader/msg-3`
---

## 🔹 📊 Flujo de Datos (Diagrama ASCII)

```
[Paciente + Encounter]
          │
          ▼
   [MessageHeader]  →  [Bundle tipo transaction]
          │
          ▼
       [HSB]  (simula envío)
          │
          ▼
     [HAPI FHIR]  (registro final)
```

---

## 🔹 Información Adicional

* **HAPI FHIR**: Servidor FHIR para pruebas y almacenamiento de recursos.
* **HSB Simulator**: Reenvía bundles tipo `transaction` o `batch` al servidor FHIR.
* **Docker Compose**: Facilita levantar y bajar ambos servicios.
