#!/bin/bash
# Script para ejecutar tests

# Activar entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: No se encontró el entorno virtual."
    exit 1
fi

echo "Ejecutando tests..."

# Ejecutar linters
echo "\n=== Ejecutando linters ==="
black --check .
isort --check-only .
flake8 .

# Ejecutar type checking
echo "\n=== Ejecutando type checking ==="
mypy .

# Ejecutar tests
echo "\n=== Ejecutando tests unitarios ==="
pytest -v --cov=agentGemini --cov-report=term-missing

echo "\n=== Tests completados ==="
