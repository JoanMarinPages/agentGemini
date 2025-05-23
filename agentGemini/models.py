"""
Modelos de datos para AgentGemini.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class CustomerType(str, Enum):
    """Tipos de cliente."""
    PARTICULAR = "particular"
    EMPRESA = "empresa"
    COOPERATIVA = "cooperativa"
    AUTONOMO = "autonomo"

class ProductCategory(str, Enum):
    """Categorías principales de productos."""
    TRACTORES = "tractores"
    COSECHADORAS = "cosechadoras"
    IMPLEMENTOS = "implementos"
    GANADERIA = "ganaderia"
    FORESTAL = "forestal"
    JARDINERIA = "jardineria"
    RECAMBIOS = "recambios"
    SERVICIOS = "servicios"

class Customer(BaseModel):
    """Modelo de cliente."""
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    customer_type: CustomerType = CustomerType.PARTICULAR
    sector: Optional[str] = None
    location: Optional[str] = None
    hectares: Optional[float] = None
    main_crops: List[str] = Field(default_factory=list)
    current_machinery: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    total_purchases: float = 0.0
    loyalty_points: int = 0
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def is_loyal_customer(self) -> bool:
        """Determina si es un cliente leal basado en compras totales."""
        return self.total_purchases >= 10000  # EUR

class Product(BaseModel):
    """Modelo de producto."""
    id: str
    name: str
    category: ProductCategory
    brand: str
    model: Optional[str] = None
    description: str
    price: float
    currency: str = "EUR"
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    specifications: Dict[str, Any] = Field(default_factory=dict)
    stock: int = 0
    lead_time_days: Optional[int] = None
    warranty_months: int = 24
    financing_available: bool = True
    
    @property
    def is_available(self) -> bool:
        """Verifica si el producto está disponible."""
        return self.stock > 0 or self.lead_time_days is not None

class CartItem(BaseModel):
    """Item en el carrito."""
    product: Product
    quantity: int = 1
    notes: Optional[str] = None
    
    @property
    def subtotal(self) -> float:
        """Calcula el subtotal del item."""
        return self.product.price * self.quantity

class Cart(BaseModel):
    """Carrito de compras."""
    items: List[CartItem] = Field(default_factory=list)
    discount_codes: List[str] = Field(default_factory=list)
    
    @property
    def total_items(self) -> int:
        """Número total de items."""
        return sum(item.quantity for item in self.items)
    
    @property
    def subtotal(self) -> float:
        """Subtotal sin descuentos."""
        return sum(item.subtotal for item in self.items)
    
    def add_item(self, product: Product, quantity: int = 1) -> None:
        """Añade un producto al carrito."""
        # Buscar si ya existe
        for item in self.items:
            if item.product.id == product.id:
                item.quantity += quantity
                return
        
        # Si no existe, añadir nuevo
        self.items.append(CartItem(product=product, quantity=quantity))
    
    def remove_item(self, product_id: str) -> bool:
        """Elimina un producto del carrito."""
        for i, item in enumerate(self.items):
            if item.product.id == product_id:
                del self.items[i]
                return True
        return False

class ServiceBooking(BaseModel):
    """Reserva de servicio."""
    id: str
    customer_id: str
    service_type: str
    product_id: Optional[str] = None
    scheduled_date: datetime
    duration_minutes: int = 60
    location: str
    notes: Optional[str] = None
    status: str = "scheduled"

class SessionState(BaseModel):
    """Estado de la sesión del agente."""
    customer: Optional[Customer] = None
    cart: Cart = Field(default_factory=Cart)
    current_category: Optional[ProductCategory] = None
    search_query: Optional[str] = None
    viewed_products: List[str] = Field(default_factory=list)
    conversation_stage: str = "greeting"
    language: str = "es"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado a diccionario."""
        return self.model_dump(exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        """Crea una instancia desde un diccionario."""
        return cls(**data)