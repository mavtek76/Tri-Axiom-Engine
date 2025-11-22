# Use official Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy local code into container
COPY tri_axiom_engine/ ./tri_axiom_engine/
COPY app.py .

# Install FastAPI and Uvicorn
RUN pip install --no-cache-dir fastapi uvicorn

# Expose port
EXPOSE 8000

# Run the API with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
