FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd -r sovereign && useradd -r -g sovereign -s /sbin/nologin sovereign \
    && mkdir -p /app/templates /app/plugins \
    && chown -R sovereign:sovereign /app

COPY config.yaml /app/config.yaml
COPY templates /app/templates
COPY plugins /app/plugins

RUN chown -R sovereign:sovereign /app
USER sovereign

ENV PYTHONPATH=/app
ENV SOVEREIGN_CONFIG=file:///app/config.yaml

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8080/healthcheck || exit 1

EXPOSE 8080

CMD ["uvicorn", "sovereign.app:app", "--host", "0.0.0.0", "--port", "8080"]
