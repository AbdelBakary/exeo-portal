# Test Dockerfile pour Railway - Version 3 (22/09/2025 12:15)
FROM python:3.11-slim

# Installer curl pour health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier l'application de test
COPY test_app.py /app/

# Exposer le port
EXPOSE $PORT

# Health check simple
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Démarrer l'application de test
CMD python test_app.py
