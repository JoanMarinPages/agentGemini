#!/bin/bash
# Script para ejecutar el agente en modo desarrollo

# Activar entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: No se encontró el entorno virtual. Ejecuta scripts/setup.sh primero."
    exit 1
fi

# Verificar archivo .env
if [ ! -f ".env" ]; then
    echo "Error: No se encontró el archivo .env"
    exit 1
fi

# Cargar variables de entorno
export $(cat .env | grep -v '^#' | xargs)

# Ejecutar con ADK
echo "Iniciando agente en modo desarrollo..."
adk run agent.py --debug --reload
