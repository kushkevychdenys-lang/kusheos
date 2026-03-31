# Multi-stage build pro menší finální image
FROM python:3.11-slim as builder

WORKDIR /app

# Instalace závislostí do tmp
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Finální stage
FROM python:3.11-slim

WORKDIR /app

# Kopíruj instalované balíčky z builderu
COPY --from=builder /root/.local /root/.local

# Kopíruj aplikaci
COPY app.py .
COPY templates/ templates/
COPY docs/ docs/

# Nastavení PATH
ENV PATH=/root/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8081/ping')" || exit 1

# Exponuj port
EXPOSE 8081

# Spuštění aplikace
CMD ["python", "app.py"]
