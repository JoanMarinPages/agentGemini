#!/bin/bash
# Script de configuración inicial para el proyecto agentGemini

echo "=== Configuración de agentGemini ==="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado."
    exit 1
fi

echo "Python encontrado: $(python3 --version)"

# Crear entorno virtual
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Copiar archivo de configuración
if [ ! -f ".env" ]; then
    echo "Creando archivo .env..."
    cp .env.example .env
    echo "Por favor, edita el archivo .env con tus credenciales."
fi

# Instalar pre-commit hooks
if command -v pre-commit &> /dev/null; then
    echo "Instalando pre-commit hooks..."
    pre-commit install
fi

echo "\n=== Configuración completada ==="
echo "Para activar el entorno virtual, ejecuta: source venv/bin/activate"
echo "Para ejecutar el agente: adk run agent.py"
