"""
Herramientas principales del agente.
"""

from .customer_tools import (
    get_customer_profile,
    update_customer_profile
)

from .catalog_tools import (
    search_products,
    get_product_details,
    get_recommendations
)

from .cart_tools import (
    add_to_cart,
    remove_from_cart,
    get_cart_summary
)

from .conversion_tools import (
    process_checkout,
    schedule_service,
    generate_discount_code
)

__all__ = [
    # Customer tools
    "get_customer_profile",
    "update_customer_profile",
    
    # Catalog tools
    "search_products",
    "get_product_details",
    "get_recommendations",
    
    # Cart tools
    "add_to_cart",
    "remove_from_cart",
    "get_cart_summary",
    
    # Conversion tools
    "process_checkout",
    "schedule_service",
    "generate_discount_code"
]