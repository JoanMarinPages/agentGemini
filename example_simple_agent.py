#!/usr/bin/env python3
"""
Ejemplo simplificado de un agente ADK siguiendo las mejores prácticas.
Basado en: https://google.github.io/adk-docs/get-started/streaming/
"""

import os
from typing import Dict, List, Any
from google.genai import Client, types
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
MODEL_NAME = "gemini-2.0-flash"


def get_weather(location: str) -> str:
    """Obtiene el clima para una ubicación (simulado)."""
    # En producción, esto llamaría a una API real
    weather_data = {
        "Barcelona": "Soleado, 22°C",
        "Madrid": "Parcialmente nublado, 18°C",
        "Granollers": "Soleado, 21°C"
    }
    return weather_data.get(location, "Información no disponible")


def search_products(query: str, category: str = None) -> List[Dict[str, Any]]:
    """Busca productos en el catálogo."""
    # Simulación de búsqueda
    products = [
        {
            "id": "tractor_001",
            "name": "Tractor Serie X",
            "category": "tractores",
            "price": 75000,
            "description": "Tractor de alta potencia para grandes extensiones"
        },
        {
            "id": "cosechadora_001",
            "name": "Cosechadora Pro Max",
            "category": "cosechadoras",
            "price": 250000,
            "description": "Cosechadora de última generación con GPS integrado"
        }
    ]
    
    # Filtrar por categoría si se especifica
    if category:
        products = [p for p in products if p["category"] == category]
    
    # Filtrar por query en nombre o descripción
    if query:
        query_lower = query.lower()
        products = [
            p for p in products 
            if query_lower in p["name"].lower() or query_lower in p["description"].lower()
        ]
    
    return products


def main():
    """Ejemplo de uso del cliente ADK con streaming."""
    
    # Crear cliente
    client = Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Definir las herramientas disponibles
    tools = [
        get_weather,
        search_products
    ]
    
    # Instrucción del sistema
    system_instruction = """
    Eres AgroAsesor, un asistente experto en maquinaria agrícola.
    Ayudas a los clientes a encontrar los mejores productos para sus necesidades.
    Eres amigable, profesional y conocedor del sector agrícola.
    
    Cuando busques productos, proporciona información detallada y relevante.
    Si el cliente menciona una ubicación, puedes consultar el clima para dar
    recomendaciones contextuales.
    """
    
    # Configuración del modelo
    config = types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=2048,
        system_instruction=system_instruction,
        tools=tools
    )
    
    # Conversación de ejemplo
    print("=== AgroAsesor - Asistente de Maquinaria Agrícola ===")
    print("\nEscribe 'salir' para terminar la conversación.\n")
    
    # Historial de la conversación
    messages = []
    
    while True:
        # Obtener input del usuario
        user_input = input("Usuario: ")
        
        if user_input.lower() == 'salir':
            print("\n¡Gracias por usar AgroAsesor! Hasta pronto.")
            break
        
        # Añadir mensaje del usuario al historial
        messages.append({"role": "user", "content": user_input})
        
        # Generar respuesta con streaming
        print("\nAgroAsesor: ", end="", flush=True)
        
        try:
            # Crear el contenido para la API
            contents = [
                types.Content(
                    role=msg["role"],
                    parts=[types.Part(text=msg["content"])]
                )
                for msg in messages
            ]
            
            # Generar respuesta
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=config,
                stream=True  # Habilitar streaming
            )
            
            # Procesar la respuesta en streaming
            full_response = ""
            for chunk in response:
                if chunk.text:
                    print(chunk.text, end="", flush=True)
                    full_response += chunk.text
            
            print()  # Nueva línea al final
            
            # Añadir respuesta del asistente al historial
            messages.append({"role": "model", "content": full_response})
            
        except Exception as e:
            print(f"\nError: {e}")
            # Remover el último mensaje del usuario si hay error
            messages.pop()
        
        print()  # Línea en blanco entre interacciones


if __name__ == "__main__":
    main()
