# Integración con Google ADK

Este documento describe cómo el proyecto agentGemini se integra con Google ADK.

## Conceptos Clave de ADK

### 1. Agentes (Agents)

Los agentes son la unidad fundamental en ADK. En nuestro proyecto:

- **`root_agent`**: El agente principal que orquesta todo el flujo
- **Sub-agentes**: Agentes especializados para tareas específicas

```python
from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="FunnelAgent",
    model="gemini-2.0-flash",
    instruction=INSTRUCTION,
    tools=[...]
)
```

### 2. Herramientas (Tools)

Las herramientas son funciones que el agente puede llamar:

```python
def get_product_details(product_id: str) -> str:
    """Obtiene detalles de un producto."""
    # Lógica de la herramienta
    return json.dumps(product_details)
```

### 3. Sesiones (Sessions)

ADK maneja el estado de la conversación a través de sesiones:

```python
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()
session = session_service.create_session(
    app_name="sales_funnel_app",
    user_id="user_123",
    session_id="session_456"
)
```

### 4. Runner

El Runner ejecuta el agente y maneja el flujo de eventos:

```python
from google.adk.runners import Runner

runner = Runner(
    agent=root_agent,
    app_name="sales_funnel_app",
    session_service=session_service
)
```

## Streaming en ADK

ADK soporta respuestas en streaming para mejor experiencia de usuario:

```python
async for event in runner.run_async(
    session_id=session.id,
    user_id=user_id,
    new_message=user_content
):
    if event.is_final_response():
        # Procesar respuesta final
        pass
    elif event.is_streaming_chunk():
        # Mostrar chunk en tiempo real
        pass
```

## Estructura del Proyecto

### Organización de Archivos

```
agentGemini/
├── agent.py          # Define root_agent
├── tools/           # Herramientas del agente
│   ├── herramientas_produccion_agroasesoria.py
│   └── tools.py
├── sub_agents/      # Sub-agentes especializados
│   ├── funnel_navigation/
│   ├── pain_point/
│   └── user_profile/
└── prompt.py        # Instrucciones del agente
```

### Flujo de Datos

1. **Usuario** envía mensaje
2. **Runner** procesa el mensaje con el agente
3. **Agente** analiza y llama herramientas si es necesario
4. **Herramientas** ejecutan lógica de negocio
5. **Agente** genera respuesta
6. **Runner** devuelve respuesta (con streaming si está habilitado)

## Mejores Prácticas

### 1. Definición de Herramientas

- Usar type hints claros
- Documentar con docstrings descriptivos
- Retornar datos estructurados (JSON/dict)

### 2. Manejo de Estado

- Usar `session.state` para datos persistentes
- Actualizar estado de forma atómica
- Validar estado antes de usarlo

### 3. Instrucciones del Agente

- Ser específico y claro
- Incluir ejemplos cuando sea posible
- Definir formato de salida esperado

### 4. Testing

```python
# tests/test_agent.py
import pytest
from agent import root_agent

@pytest.mark.asyncio
async def test_agent_response():
    # Test del agente
    pass
```

## Integración con Vertex AI

Para producción, usar `VertexAiSessionService`:

```python
from google.adk.sessions import VertexAiSessionService

session_service = VertexAiSessionService(
    project_id="your-project-id",
    location="us-central1"
)
```

## Recursos

- [Documentación oficial de ADK](https://google.github.io/adk-docs/)
- [Guía de Streaming](https://google.github.io/adk-docs/get-started/streaming/)
- [Referencia de API](https://google.github.io/adk-docs/api-reference/)
