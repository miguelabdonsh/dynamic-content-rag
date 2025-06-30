#!/bin/bash

echo "Iniciando servicios RAG..."

# Crear directorios
mkdir -p data/qdrant data/redis logs

# Ir a carpeta docker
cd docker

# Iniciar servicios
docker compose up -d

echo "Servicios iniciados!"
echo "Qdrant: http://localhost:6333"
echo "Redis: localhost:6379 (pass: ragpass123)"
echo "CrawlAI: http://localhost:11235"
echo "Para detener: ./scripts/stop-services.sh" 