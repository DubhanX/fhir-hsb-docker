FROM python:3.12-slim

WORKDIR /app

COPY bundle.json /app/bundle.json
COPY hsb.py /app/hsb.py

RUN pip install --no-cache-dir flask requests

EXPOSE 5000

CMD ["python", "hsb.py"]
