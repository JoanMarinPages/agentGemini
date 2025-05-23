"""
Herramientas para conversión y cierre de ventas.
"""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ..models import Cart, ServiceBooking
from ..config import Config
from ..services.firestore_service import FirestoreService
from ..services.email_service import EmailService

logger = logging.getLogger(__name__)

db_service = FirestoreService()
email_service = EmailService()

def process_checkout(
    session_state: Dict[str, Any],
    payment_method: str,
    delivery_address: Optional[Dict[str, Any]] = None,
    billing_info: Optional[Dict[str, Any]] = None,
    special_instructions: Optional[str] = None
) -> Dict[str, Any]:
    """
    Procesa el checkout y crea el pedido.
    
    Args:
        session_state: Estado de la sesión con carrito y cliente
        payment_method: Método de pago (transfer, financing, card)
        delivery_address: Dirección de entrega
        billing_info: Información de facturación
        special_instructions: Instrucciones especiales
        
    Returns:
        Dict con el resultado del checkout
    """
    try:
        # Validar carrito
        cart_data = session_state.get("cart", {})
        if not cart_data or not cart_data.get("items"):
            return {
                "status": "error",
                "message": "El carrito está vacío"
            }
        
        cart = Cart(**cart_data)
        
        # Validar cliente
        customer = session_state.get("customer")
        if not customer:
            return {
                "status": "error",
                "message": "Debe identificarse antes de proceder al pago"
            }
        
        # Validar método de pago
        valid_methods = ["transfer", "financing", "card"]
        if payment_method not in valid_methods:
            return {
                "status": "error",
                "message": f"Método de pago inválido. Opciones: {', '.join(valid_methods)}"
            }
        
        # Crear pedido
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        order_data = {
            "id": order_id,
            "customer_id": customer.get("id"),
            "customer_name": customer.get("name"),
            "customer_email": customer.get("email"),
            "items": [
                {
                    "product_id": item["product"]["id"],
                    "name": item["product"]["name"],
                    "quantity": item["quantity"],
                    "unit_price": item["product"]["price"],
                    "subtotal": item["product"]["price"] * item["quantity"]
                }
                for item in cart_data["items"]
            ],
            "subtotal": cart.subtotal,
            "discount_codes": cart.discount_codes,
            "discount_amount": 0,  # Calcular según códigos
            "total": cart.subtotal,
            "currency": Config.DEFAULT_CURRENCY,
            "payment_method": payment_method,
            "delivery_address": delivery_address,
            "billing_info": billing_info,
            "special_instructions": special_instructions,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Aplicar descuento por lealtad si aplica
        if customer.get("total_purchases", 0) >= Config.LOYALTY_DISCOUNT_THRESHOLD:
            discount = order_data["subtotal"] * (Config.LOYALTY_DISCOUNT_PERCENTAGE / 100)
            order_data["discount_amount"] = discount
            order_data["total"] = order_data["subtotal"] - discount
            order_data["discount_reason"] = "Descuento cliente leal"
        
        # Guardar pedido en Firestore
        db_service.create_order(order_data)
        
        # Actualizar total de compras del cliente
        new_total = customer.get("total_purchases", 0) + order_data["total"]
        db_service.update_customer(
            customer["id"],
            {"total_purchases": new_total}
        )
        
        # Enviar email de confirmación
        if customer.get("email"):
            email_service.send_order_confirmation(
                customer["email"],
                order_data
            )
        
        # Limpiar carrito
        session_state["cart"] = Cart().model_dump()
        
        logger.info(f"Pedido creado: {order_id} para cliente {customer['id']}")
        
        return {
            "status": "success",
            "message": "Pedido procesado correctamente",
            "order_id": order_id,
            "order_summary": {
                "total": order_data["total"],
                "currency": order_data["currency"],
                "payment_method": payment_method,
                "estimated_delivery": (
                    datetime.now() + timedelta(days=7)
                ).strftime("%d/%m/%Y")
            },
            "next_steps": _get_next_steps(payment_method)
        }
        
    except Exception as e:
        logger.error(f"Error procesando checkout: {e}")
        return {
            "status": "error",
            "message": "Error al procesar el pedido"
        }

def schedule_service(
    customer_id: str,
    service_type: str,
    preferred_date: str,
    location: str,
    product_id: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Programa un servicio técnico o demostración.
    
    Args:
        customer_id: ID del cliente
        service_type: Tipo de servicio (demo, installation, maintenance)
        preferred_date: Fecha preferida (YYYY-MM-DD)
        location: Ubicación del servicio
        product_id: ID del producto relacionado
        notes: Notas adicionales
        
    Returns:
        Dict con la confirmación de la cita
    """
    try:
        # Validar tipo de servicio
        valid_services = ["demo", "installation", "maintenance", "training"]
        if service_type not in valid_services:
            return {
                "status": "error",
                "message": f"Tipo de servicio inválido. Opciones: {', '.join(valid_services)}"
            }
        
        # Validar fecha
        try:
            service_date = datetime.strptime(preferred_date, "%Y-%m-%d")
            if service_date < datetime.now():
                return {
                    "status": "error",
                    "message": "La fecha debe ser futura"
                }
            
            max_date = datetime.now() + timedelta(days=Config.SERVICE_BOOKING_DAYS_AHEAD)
            if service_date > max_date:
                return {
                    "status": "error",
                    "message": f"Solo se pueden programar servicios hasta {Config.SERVICE_BOOKING_DAYS_AHEAD} días en adelante"
                }
        except ValueError:
            return {
                "status": "error",
                "message": "Formato de fecha inválido. Use YYYY-MM-DD"
            }
        
        # Verificar disponibilidad (simplificado)
        # En producción, esto verificaría contra un calendario real
        if service_date.weekday() in [5, 6]:  # Sábado o domingo
            return {
                "status": "error",
                "message": "No hay servicio disponible los fines de semana"
            }
        
        # Crear reserva
        booking_id = f"SVC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        booking = ServiceBooking(
            id=booking_id,
            customer_id=customer_id,
            service_type=service_type,
            product_id=product_id,
            scheduled_date=service_date,
            duration_minutes=Config.SERVICE_DURATION_MINUTES,
            location=location,
            notes=notes,
            status="scheduled"
        )
        
        # Guardar en Firestore
        db_service.create_service_booking(booking.model_dump())
        
        # Obtener info del cliente para enviar confirmación
        customer = db_service.get_customer(customer_id)
        
        # Enviar confirmación por email
        if customer and customer.get("email"):
            email_service.send_service_confirmation(
                customer["email"],
                booking.model_dump()
            )
        
        logger.info(f"Servicio programado: {booking_id} para cliente {customer_id}")
        
        # Descripción del servicio
        service_descriptions = {
            "demo": "Demostración de producto",
            "installation": "Instalación y puesta en marcha",
            "maintenance": "Mantenimiento preventivo",
            "training": "Formación de operarios"
        }
        
        return {
            "status": "success",
            "message": "Servicio programado correctamente",
            "booking_id": booking_id,
            "booking_details": {
                "service": service_descriptions.get(service_type, service_type),
                "date": service_date.strftime("%d/%m/%Y"),
                "time": "Por confirmar",  # En producción, incluiría hora específica
                "location": location,
                "duration": f"{Config.SERVICE_DURATION_MINUTES} minutos",
                "technician": "Por asignar"
            },
            "next_steps": [
                "Recibirás un email de confirmación",
                "Un técnico te contactará 24h antes para confirmar la hora",
                "Prepara el área donde se realizará el servicio"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error programando servicio: {e}")
        return {
            "status": "error",
            "message": "Error al programar el servicio"
        }

def generate_discount_code(
    customer_id: str,
    discount_type: str = "loyalty",
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Genera un código de descuento para el cliente.
    
    Args:
        customer_id: ID del cliente
        discount_type: Tipo de descuento (loyalty, new_customer, referral)
        reason: Razón del descuento
        
    Returns:
        Dict con el código de descuento generado
    """
    try:
        # Obtener información del cliente
        customer = db_service.get_customer(customer_id)
        if not customer:
            return {
                "status": "error",
                "message": "Cliente no encontrado"
            }
        
        # Determinar el porcentaje de descuento
        discount_percentages = {
            "loyalty": Config.LOYALTY_DISCOUNT_PERCENTAGE,
            "new_customer": Config.NEW_CUSTOMER_DISCOUNT_PERCENTAGE,
            "referral": 15,
            "seasonal": 10
        }
        
        percentage = discount_percentages.get(discount_type, 5)
        
        # Verificar elegibilidad
        if discount_type == "loyalty":
            if customer.get("total_purchases", 0) < Config.LOYALTY_DISCOUNT_THRESHOLD:
                return {
                    "status": "error",
                    "message": f"Se requieren compras por {Config.LOYALTY_DISCOUNT_THRESHOLD}€ para descuento de lealtad"
                }
        
        elif discount_type == "new_customer":
            if customer.get("total_purchases", 0) > 0:
                return {
                    "status": "error",
                    "message": "Este descuento es solo para nuevos clientes"
                }
        
        # Generar código único
        code = f"{discount_type.upper()}-{uuid.uuid4().hex[:8].upper()}"
        
        # Crear registro del descuento
        discount_data = {
            "code": code,
            "customer_id": customer_id,
            "type": discount_type,
            "percentage": percentage,
            "reason": reason or f"Descuento {discount_type}",
            "valid_from": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
            "used": False,
            "created_at": datetime.now().isoformat()
        }
        
        # Guardar en Firestore
        db_service.create_discount_code(discount_data)
        
        logger.info(f"Código de descuento generado: {code} para cliente {customer_id}")
        
        return {
            "status": "success",
            "message": "Código de descuento generado",
            "discount_code": {
                "code": code,
                "percentage": percentage,
                "valid_until": (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y"),
                "conditions": _get_discount_conditions(discount_type)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generando código de descuento: {e}")
        return {
            "status": "error",
            "message": "Error al generar el código de descuento"
        }

def _get_next_steps(payment_method: str) -> List[str]:
    """Obtiene los próximos pasos según el método de pago."""
    steps = {
        "transfer": [
            "Recibirás los datos bancarios por email",
            "Realiza la transferencia en las próximas 48h",
            "Envíanos el comprobante para agilizar el proceso",
            "Una vez confirmado el pago, procesaremos tu pedido"
        ],
        "financing": [
            "Recibirás un email con el enlace a la solicitud",
            "Completa la documentación requerida",
            "Respuesta de aprobación en 24-48h",
            "Una vez aprobado, coordinaremos la entrega"
        ],
        "card": [
            "El pago ha sido procesado correctamente",
            "Recibirás la factura por email",
            "Preparamos tu pedido para envío",
            "Te notificaremos cuando esté en camino"
        ]
    }
    return steps.get(payment_method, [])

def _get_discount_conditions(discount_type: str) -> List[str]:
    """Obtiene las condiciones del descuento."""
    conditions = {
        "loyalty": [
            "Válido para tu próxima compra",
            "No acumulable con otras ofertas",
            "Aplicable a todos los productos"
        ],
        "new_customer": [
            "Solo para primera compra",
            "Mínimo de compra: 1000€",
            "No aplicable a servicios"
        ],
        "referral": [
            "Válido cuando tu referido realice su primera compra",
            "Acumulable hasta 3 referidos",
            "Aplicable a productos seleccionados"
        ],
        "seasonal": [
            "Válido durante la temporada actual",
            "Aplicable a maquinaria en stock",
            "No acumulable con financiación"
        ]
    }
    return conditions.get(discount_type, ["Consulta condiciones específicas"])