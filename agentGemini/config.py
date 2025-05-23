"""
Configuración central para AgentGemini.
"""

import os
from typing import Optional

class Config:
    """Configuración del agente."""
    
    # Modelo
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash")
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true"
    
    # Firebase/Firestore
    FIRESTORE_DATABASE = os.getenv("FIRESTORE_DATABASE", "(default)")
    
    # Configuración del agente
    MAX_CART_ITEMS = 50
    DEFAULT_CURRENCY = "EUR"
    DEFAULT_LANGUAGE = "es"
    
    # Descuentos
    LOYALTY_DISCOUNT_THRESHOLD = 1000  # EUR
    LOYALTY_DISCOUNT_PERCENTAGE = 10
    NEW_CUSTOMER_DISCOUNT_PERCENTAGE = 5
    
    # Servicios
    SERVICE_BOOKING_DAYS_AHEAD = 30
    SERVICE_DURATION_MINUTES = 60
    
    # Cache
    CACHE_TTL_SECONDS = 3600  # 1 hora
    
    @classmethod
    def validate(cls) -> bool:
        """Valida que la configuración requerida esté presente."""
        required = []
        
        if cls.GOOGLE_GENAI_USE_VERTEXAI:
            required.extend(["GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION"])
        
        missing = [var for var in required if not os.getenv(var)]
        
        if missing:
            raise ValueError(f"Variables de entorno faltantes: {', '.join(missing)}")
        
        return True