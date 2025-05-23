#!/usr/bin/env python3
"""
Agente principal de AgentGemini usando Google ADK.
Basado en las mejores prácticas del ejemplo customer-service.
"""

import os
import logging
from typing import Dict, Any, Optional
from google.genai.adk import Agent
from dotenv import load_dotenv

from .config import Config
from .models import SessionState
from .tools import (
    get_customer_profile,
    update_customer_profile,
    search_products,
    get_product_details,
    add_to_cart,
    remove_from_cart,
    get_cart_summary,
    process_checkout,
    get_recommendations,
    schedule_service,
    generate_discount_code
)
from .prompts import MAIN_INSTRUCTION

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Crear el agente principal
root_agent = Agent(
    name="AgroAsesorIA",
    model=Config.MODEL_NAME,
    description="Agente experto en maquinaria agrícola y soluciones para el campo",
    instruction=MAIN_INSTRUCTION,
    tools=[
        # Herramientas de perfil de cliente
        get_customer_profile,
        update_customer_profile,
        
        # Herramientas de catálogo
        search_products,
        get_product_details,
        get_recommendations,
        
        # Herramientas de carrito
        add_to_cart,
        remove_from_cart,
        get_cart_summary,
        
        # Herramientas de conversión
        process_checkout,
        schedule_service,
        generate_discount_code
    ],
    initial_state=SessionState().to_dict()
)

# Configurar callbacks para eventos
@root_agent.on_tool_call
def log_tool_call(tool_name: str, args: Dict[str, Any]):
    """Log cuando se llama una herramienta."""
    logger.info(f"Llamando herramienta: {tool_name} con args: {args}")

@root_agent.on_response
def log_response(response: str):
    """Log de las respuestas del agente."""
    logger.info(f"Respuesta del agente: {response[:100]}...")

if __name__ == "__main__":
    # Para testing local
    print("AgentGemini está listo para ejecutarse con 'adk run' o 'adk web'")