FROM mcr.microsoft.com/mirror/docker/library/python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# dependencias del sistema (solo cuando cambian los paquetes APT)
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    rm -rf /var/lib/apt/lists/*
    
# ---------------------------------------
# Capa de dependencias Python
# ---------------------------------------
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# ---------------------------------------
# Código de la aplicación
# ---------------------------------------
COPY . .

CMD ["python", "run_all_ingestors.py"]
