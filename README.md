# Agent Gemini

Un agente inteligente construido con Google ADK (Agent Development Kit) para procesamiento avanzado de tareas en el sector agrícola.

## Descripción

Este proyecto implementa un agente de ventas inteligente para Agriland que guía a los usuarios a través de un embudo de ventas personalizado, ayudándoles a encontrar la maquinaria agrícola y soluciones perfectas para sus necesidades.

## Características

- **Perfilado de usuarios**: Recopilación progresiva de información del cliente
- **Navegación inteligente**: Guía a través de categorías y productos
- **Identificación de necesidades**: Detecta puntos de dolor y sugiere soluciones
- **Integración con Firestore**: Persistencia de datos y perfiles
- **Streaming de respuestas**: Respuestas en tiempo real con ADK

## Estructura del Proyecto

```
agentGemini/
├── agent.py           # Agente principal con LlmAgent
├── constants.py       # Constantes y configuración
├── prompt.py         # Prompts e instrucciones del agente
├── entities/         # Modelos de datos
├── sub_agents/       # Sub-agentes especializados
├── tools/           # Herramientas y funciones
└── shared_libraries/ # Código compartido
```

## Instalación

### Prerequisitos

- Python 3.8+
- Cuenta de Google Cloud con acceso a Vertex AI
- ADK instalado

### Pasos de instalación

1. Clona el repositorio:
```bash
git clone https://github.com/JoanMarinPages/agentGemini.git
cd agentGemini
```

2. Crea un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Configura las variables de entorno:
```bash
cp .env.example .env
# Edita .env con tus credenciales
```

## Uso

### Ejecutar con ADK CLI

```bash
# Modo desarrollo con streaming
adk run agent.py

# Modo web interface
adk web agent.py
```

### Ejecutar directamente

```bash
python -m agent
```

## Configuración

El agente utiliza las siguientes variables de entorno:

- `GOOGLE_APPLICATION_CREDENTIALS`: Path a las credenciales de GCP
- `PROJECT_ID`: ID del proyecto de Google Cloud
- `GEMINI_API_KEY`: API key para Gemini (opcional)
- `FIRESTORE_DATABASE`: Nombre de la base de datos de Firestore

## Desarrollo

### Estructura de un Agente ADK

```python
from google.adk.agents import LlmAgent

# Definir el agente principal
root_agent = LlmAgent(
    name="AgentName",
    model="gemini-2.0-flash",
    instruction="Instrucciones del agente...",
    tools=[...]
)
```

### Añadir nuevas herramientas

Las herramientas deben seguir el formato ADK:

```python
def mi_herramienta(param: str) -> str:
    """Descripción de la herramienta."""
    # Lógica de la herramienta
    return resultado
```

## Testing

```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=agentGemini
```

## Contribuciones

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para detalles sobre cómo contribuir.

## Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## Enlaces Útiles

- [Documentación de ADK](https://google.github.io/adk-docs/)
- [Guía de Streaming](https://google.github.io/adk-docs/get-started/streaming/)
- [Vertex AI](https://cloud.google.com/vertex-ai)