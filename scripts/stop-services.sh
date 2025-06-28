#!/bin/bash

echo "Deteniendo servicios RAG..."

# Ir a carpeta docker
cd docker

# Detener servicios
docker compose down

echo "Servicios detenidos!"
echo "Para reiniciar: ./scripts/start-services.sh" 