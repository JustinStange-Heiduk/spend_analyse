# Minimaler Python-Container
FROM python:3.11-slim

# Systemabhängigkeiten für paramiko
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ssh-client \
 && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis setzen
WORKDIR /workspace

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


