# Agent Gemini

Un agente inteligente construido con ADK (Agent Development Kit) para procesamiento avanzado de tareas.

## Estructura del Proyecto

```
agentGemini/
├── agent.py           # Agente principal
├── constants.py       # Constantes del proyecto
├── prompt.py         # Gestión de prompts
├── entities/         # Entidades del dominio
├── sub_agents/       # Sub-agentes especializados
├── tools/           # Herramientas y utilidades
└── shared_libraries/ # Bibliotecas compartidas
```

## Instalación

1. Clona este repositorio:
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

## Configuración

1. Copia el archivo `.env.example` a `.env`
2. Configura las variables de entorno necesarias

## Uso

```bash
python agent.py
```

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

## Licencia

Este proyecto está bajo la Licencia MIT.
