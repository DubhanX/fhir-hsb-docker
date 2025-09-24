# Laboratorio de Mensajería FHIR con Health Service Bus (HSB)

Este repositorio contiene la implementación de un Health Service Bus (HSB) para un laboratorio de la materia de Sistemas Distribuidos. El objetivo es demostrar la mensajería entre sistemas de salud utilizando el estándar FHIR, orquestado a través de contenedores de Docker.

El proyecto simula un flujo donde un paquete de recursos FHIR (un `Bundle`) es recibido por un bus de servicios (nuestra aplicación en Flask) y luego persistido en un servidor FHIR de referencia (HAPI FHIR).

## 📝 Descripción del Laboratorio

El laboratorio se centra en los siguientes pasos conceptuales, basados en el estándar de mensajería de FHIR:

1.  **Crear un `MessageHeader`**: Se define un encabezado de mensaje que actúa como el punto de entrada y metadato principal de la comunicación.
2.  **Empaquetar en un `Bundle`**: Se agrupan múltiples recursos de FHIR (como `Patient`, `Encounter` y el `MessageHeader`) en un `Bundle` de tipo `message`. Este paquete representa una unidad de trabajo completa.
3.  **Enviar al HSB**: El `Bundle` es enviado a nuestro Health Service Bus, que actúa como intermediario.
4.  **Procesar y Almacenar**: El HSB descompone el `Bundle` y guarda cada recurso individualmente en el servidor HAPI FHIR para su persistencia y futura consulta.

## 🛠️ Arquitectura y Tecnologías

El proyecto está completamente contenedorizado usando Docker y se compone de los siguientes servicios:

-   **`hsb` (Health Service Bus)**:
    -   **Descripción**: Una aplicación web ligera desarrollada en Python con **Flask**.
    -   **Función**: Expone un endpoint `/hsb` que recibe los `Bundles` de FHIR. Procesa cada recurso del `Bundle` y lo envía mediante una petición `PUT` al servidor HAPI FHIR.
    -   **Tecnologías**: Python, Flask, Requests.

-   **`hapi-fhir`**:
    -   **Descripción**: Una instancia del popular servidor de referencia HAPI FHIR.
    -   **Función**: Actúa como el repositorio central y persistente para los recursos de FHIR. Proporciona una API RESTful completa para interactuar con los datos.
    -   **Tecnologías**: HAPI FHIR (Java).

-   **Red**:
    -   Ambos servicios se comunican a través de una red interna de Docker (`fhir-net`), lo que permite que el servicio `hsb` se conecte con `hapi-fhir` usando el nombre del contenedor como hostname.

## 🚀 Cómo Ejecutar el Proyecto

Sigue estos pasos para levantar el entorno y probar el flujo completo.

### Prerrequisitos

-   Tener [Docker](https://www.docker.com/get-started) y [Docker Compose](https://docs.docker.com/compose/install/) instalados.

### 1. Iniciar los Servicios

Abre una terminal en la raíz del proyecto y ejecuta el siguiente comando para construir las imágenes y levantar los contenedores en segundo plano:

```bash
docker-compose up -d --build
```

Este comando hará lo siguiente:
-   Descargará la imagen de `hapiproject/hapi:latest`.
-   Construirá la imagen para el servicio `hsb` según el `Dockerfile`.
-   Iniciará ambos contenedores y los conectará a la red `fhir-net`.

Puedes verificar que los contenedores estén en ejecución con `docker ps`.

### 2. Enviar el Mensaje al HSB

Una vez que los servicios estén listos (HAPI FHIR puede tardar un minuto en arrancar completamente), envía el `Bundle` de ejemplo (`bundle.json`) a nuestro HSB.

Abre otra terminal y ejecuta el siguiente comando `curl`:

```bash
curl -X POST -H "Content-Type: application/json" --data @bundle.json http://localhost:5000/hsb
```

Si la operación es exitosa, recibirás una respuesta como esta:

```json
{
  "status": "Bundle enviado a HAPI"
}
```

### 3. Verificar los Recursos en HAPI FHIR

El HSB ha procesado el `Bundle` y enviado los recursos a HAPI FHIR. Puedes verificar que los recursos existen accediendo a las siguientes URLs en tu navegador:

-   **Paciente**: [http://localhost:8080/fhir/Patient/p1](http://localhost:8080/fhir/Patient/p1)
-   **Encuentro**: [http://localhost:8080/fhir/Encounter/e1](http://localhost:8080/fhir/Encounter/e1)
-   **Encabezado del Mensaje**: [http://localhost:8080/fhir/MessageHeader/m1](http://localhost:8080/fhir/MessageHeader/m1)

Si puedes ver los datos en formato JSON en cada una de estas URLs, ¡el laboratorio ha sido completado con éxito!

## 📂 Estructura del Repositorio

-   `README.md`: Este archivo.
-   `docker-compose.yml`: Orquesta el despliegue de los servicios `hsb` y `hapi-fhir`.
-   `Dockerfile`: Define la imagen de Docker para el servicio `hsb`.
-   `hsb.py`: El código fuente de la aplicación Flask que funciona como HSB.
-   `bundle.json`: Un `Bundle` de FHIR de ejemplo con los recursos a procesar.
