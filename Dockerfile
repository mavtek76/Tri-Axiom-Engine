FROM python:3.11-slim

# Non-root user
RUN useradd -m appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy engine + proxy
COPY engine/ ./engine/
COPY proxy/ ./proxy/

USER appuser

EXPOSE 8080

CMD ["uvicorn", "proxy.server:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
