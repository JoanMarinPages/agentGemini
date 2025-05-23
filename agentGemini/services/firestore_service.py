"""
Servicio para interactuar con Firestore.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

from ..config import Config

logger = logging.getLogger(__name__)

class FirestoreService:
    """
    Servicio para operaciones con Firestore.
    """
    
    def __init__(self):
        """Inicializa la conexión con Firestore."""
        try:
            # Inicializar Firebase si no está ya inicializado
            if not firebase_admin._apps:
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred, {
                    'projectId': Config.GOOGLE_CLOUD_PROJECT,
                })
            
            self.db = firestore.client(database=Config.FIRESTORE_DATABASE)
            logger.info("Firestore inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando Firestore: {e}")
            # En desarrollo, usar mock
            self.db = None
    
    # Métodos para Clientes
    
    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un cliente por ID."""
        if not self.db:
            return self._mock_customer(customer_id)
        
        try:
            doc = self.db.collection('customers').document(customer_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"Error obteniendo cliente {customer_id}: {e}")
            return None
    
    def get_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca un cliente por email."""
        if not self.db:
            return self._mock_customer_by_email(email)
        
        try:
            customers = self.db.collection('customers')\
                .where('email', '==', email)\
                .limit(1)\
                .get()
            
            for doc in customers:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            
            return None
        except Exception as e:
            logger.error(f"Error buscando cliente por email {email}: {e}")
            return None
    
    def create_customer(self, customer_data: Dict[str, Any]) -> str:
        """Crea un nuevo cliente."""
        if not self.db:
            return f"cust_{datetime.now().timestamp()}"
        
        try:
            doc_ref = self.db.collection('customers').document()
            customer_data['created_at'] = firestore.SERVER_TIMESTAMP
            doc_ref.set(customer_data)
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error creando cliente: {e}")
            raise
    
    def update_customer(self, customer_id: str, updates: Dict[str, Any]) -> None:
        """Actualiza un cliente."""
        if not self.db:
            return
        
        try:
            updates['updated_at'] = firestore.SERVER_TIMESTAMP
            self.db.collection('customers').document(customer_id).update(updates)
        except Exception as e:
            logger.error(f"Error actualizando cliente {customer_id}: {e}")
            raise
    
    # Métodos para Productos
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por ID."""
        if not self.db:
            return self._mock_product(product_id)
        
        try:
            doc = self.db.collection('products').document(product_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"Error obteniendo producto {product_id}: {e}")
            return None
    
    def search_products(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Busca productos según criterios."""
        if not self.db:
            return self._mock_search_products()
        
        try:
            collection = self.db.collection('products')
            
            # Aplicar filtros
            if filters:
                for field, value in filters.items():
                    if isinstance(value, dict) and '>' in value:
                        collection = collection.where(field, '>', value['>'])
                    else:
                        collection = collection.where(field, '==', value)
            
            if min_price is not None:
                collection = collection.where('price', '>=', min_price)
            
            if max_price is not None:
                collection = collection.where('price', '<=', max_price)
            
            # Limitar resultados
            collection = collection.limit(limit)
            
            # Ejecutar query
            docs = collection.get()
            
            products = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Filtrar por query de texto si existe
                if query:
                    query_lower = query.lower()
                    if (query_lower in data.get('name', '').lower() or
                        query_lower in data.get('description', '').lower()):
                        products.append(data)
                else:
                    products.append(data)
            
            return products[:limit]
            
        except Exception as e:
            logger.error(f"Error buscando productos: {e}")
            return []
    
    # Métodos para Pedidos
    
    def create_order(self, order_data: Dict[str, Any]) -> str:
        """Crea un nuevo pedido."""
        if not self.db:
            return order_data.get('id', f"order_{datetime.now().timestamp()}")
        
        try:
            order_id = order_data.get('id')
            if order_id:
                doc_ref = self.db.collection('orders').document(order_id)
            else:
                doc_ref = self.db.collection('orders').document()
                order_data['id'] = doc_ref.id
            
            order_data['created_at'] = firestore.SERVER_TIMESTAMP
            doc_ref.set(order_data)
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error creando pedido: {e}")
            raise
    
    # Métodos para Servicios
    
    def create_service_booking(self, booking_data: Dict[str, Any]) -> str:
        """Crea una reserva de servicio."""
        if not self.db:
            return booking_data.get('id', f"booking_{datetime.now().timestamp()}")
        
        try:
            booking_id = booking_data.get('id')
            if booking_id:
                doc_ref = self.db.collection('service_bookings').document(booking_id)
            else:
                doc_ref = self.db.collection('service_bookings').document()
                booking_data['id'] = doc_ref.id
            
            booking_data['created_at'] = firestore.SERVER_TIMESTAMP
            doc_ref.set(booking_data)
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error creando reserva de servicio: {e}")
            raise
    
    # Métodos para Códigos de Descuento
    
    def create_discount_code(self, discount_data: Dict[str, Any]) -> str:
        """Crea un código de descuento."""
        if not self.db:
            return discount_data.get('code', f"DISC-{datetime.now().timestamp()}")
        
        try:
            code = discount_data.get('code')
            doc_ref = self.db.collection('discount_codes').document(code)
            discount_data['created_at'] = firestore.SERVER_TIMESTAMP
            doc_ref.set(discount_data)
            return code
        except Exception as e:
            logger.error(f"Error creando código de descuento: {e}")
            raise
    
    # Métodos Mock para desarrollo
    
    def _mock_customer(self, customer_id: str) -> Dict[str, Any]:
        """Cliente mock para desarrollo."""
        return {
            "id": customer_id,
            "name": "Juan Pérez",
            "email": "juan@example.com",
            "phone": "+34 600 123 456",
            "customer_type": "particular",
            "sector": "olivar",
            "location": "Jaén",
            "hectares": 150,
            "total_purchases": 15000,
            "created_at": "2024-01-15T10:00:00"
        }
    
    def _mock_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca cliente mock por email."""
        if email == "juan@example.com":
            return self._mock_customer("cust_123")
        return None
    
    def _mock_product(self, product_id: str) -> Dict[str, Any]:
        """Producto mock para desarrollo."""
        products = {
            "tractor_x1000": {
                "id": "tractor_x1000",
                "name": "Tractor Serie X1000",
                "category": "tractores",
                "brand": "John Deere",
                "model": "X1000",
                "description": "Tractor de alta potencia ideal para grandes explotaciones",
                "price": 75000,
                "currency": "EUR",
                "stock": 3,
                "lead_time_days": 15,
                "warranty_months": 24,
                "financing_available": True,
                "specifications": {
                    "potencia": "200 CV",
                    "transmision": "PowerShift",
                    "cabina": "Con aire acondicionado"
                }
            }
        }
        return products.get(product_id, {
            "id": product_id,
            "name": "Producto Demo",
            "price": 10000
        })
    
    def _mock_search_products(self) -> List[Dict[str, Any]]:
        """Búsqueda mock de productos."""
        return [
            self._mock_product("tractor_x1000"),
            {
                "id": "cosechadora_pro",
                "name": "Cosechadora Pro Max",
                "category": "cosechadoras",
                "brand": "New Holland",
                "price": 250000,
                "stock": 1
            },
            {
                "id": "arado_3000",
                "name": "Arado Reversible 3000",
                "category": "implementos",
                "brand": "Kverneland",
                "price": 15000,
                "stock": 5
            }
        ]