FROM python:3.12-slim

WORKDIR /app

# Instalace závislostí
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopíruj aplikaci
COPY app.py .
COPY templates/ templates/
COPY docs/ docs/

EXPOSE 8081

CMD ["python", "app.py"]
