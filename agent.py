import os
import json
import datetime
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types as genai_types # Para crear el Content del usuario
from .tools import herramientas_produccion_agroasesoria
from .prompt import INSTRUCTION, pain_point, product_interaction, user_profile

# --- Constantes (ajusta según necesites) ---
APP_NAME = "sales_funnel_app"
USER_ID = "test_user_01"
SESSION_ID_BASE = "funnel_session"
GEMINI_MODEL = "gemini-2.0-flash"

# --- Estado del Embudo (claves para session.state) ---
STATE_FUNNEL_STEP = "funnel_step"
STATE_SELECTED_CATEGORY = "selected_category_id"
STATE_SELECTED_PRODUCT = "selected_product_id"

# --- IDs de Plantillas (para que el frontend sepa qué mostrar) ---
TEMPLATE_SHOW_WELCOME_CATEGORIES = "SHOW_WELCOME_CATEGORIES"
TEMPLATE_SHOW_PRODUCTS_IN_CATEGORY = "SHOW_PRODUCTS_IN_CATEGORY"
TEMPLATE_SHOW_PRODUCT_DETAILS = "SHOW_PRODUCT_DETAILS"
TEMPLATE_ASK_CLARIFICATION = "ASK_CLARIFICATION"
TEMPLATE_ERROR = "SHOW_ERROR"
initial_state = "welcom"

# --- Herramientas Simuladas (reemplazar con llamadas reales a Firestore) ---

def get_initial_categories_tool() -> str:
    """
    Simula la obtención de categorías iniciales desde Firestore.
    Devuelve una lista de categorías en formato JSON string.
    """
    print("  [Tool Call] get_initial_categories_tool")
    # En la vida real: db.collection("Categoria").where("show", "==", True).order_by("order").stream()
    categories = [
        {"id": "cat_tractors", "name": "Tractores", "description": "Potencia y eficiencia para tu campo.", "image_url": "https://example.com/tractor.jpg"},
        {"id": "cat_harvesters", "name": "Cosechadoras", "description": "Maximiza tu rendimiento en la cosecha.", "image_url": "https://example.com/harvester.jpg"},
        {"id": "cat_implements", "name": "Implementos", "description": "Herramientas versátiles para toda labor.", "image_url": "https://example.com/implement.jpg"},
    ]
    return json.dumps(categories)

def get_products_for_category_tool(category_id: str) -> str:
    """
    Simula la obtención de productos para una categoría específica desde Firestore.
    Devuelve una lista de productos en formato JSON string.
    """
    print(f"  [Tool Call] get_products_for_category_tool, category_id: {category_id}")
    # En la vida real: db.collection("Tractor").where("categoria", "==", category_id).where("show", "==", True).stream()
    products = []
    if category_id == "cat_tractors":
        products = [
            {"id": "prod_trac_001", "name": "SuperTractor X1000", "short_description": "El más vendido, ideal para grandes extensiones.", "image_url": "https://example.com/tractor_x1000.jpg", "price": "€75,000"},
            {"id": "prod_trac_002", "name": "CompactFarm 300", "short_description": "Ágil y potente para terrenos medianos.", "image_url": "https://example.com/tractor_cf300.jpg", "price": "€45,000"},
        ]
    elif category_id == "cat_harvesters":
        products = [
            {"id": "prod_harv_001", "name": "MegaHarvester Pro", "short_description": "Alta capacidad y tecnología de punta.", "image_url": "https://example.com/harvester_pro.jpg", "price": "€250,000"},
        ]
    return json.dumps(products)

def get_product_details_tool(product_id: str) -> str:
    """
    Simula la obtención de detalles de un producto específico y sus argumentos de venta.
    Devuelve un objeto de producto con detalles en formato JSON string.
    """
    print(f"  [Tool Call] get_product_details_tool, product_id: {product_id}")
    # En la vida real:
    # 1. db.collection("Tractor").document(product_id).get()
    # 2. db.collection("argumentosDeVenta").document(product_id).get()
    # ... y luego combinar los datos.
    details = {}
    if product_id == "prod_trac_001":
        details = {
            "id": "prod_trac_001",
            "name": "SuperTractor X1000",
            "description_larga": "El SuperTractor X1000 combina un motor de última generación con una cabina confortable y tecnología de agricultura de precisión. Sus 200 caballos de fuerza y bajo consumo lo hacen imparable.",
            "images": ["https://example.com/tractor_x1000_1.jpg", "https://example.com/tractor_x1000_2.jpg"],
            "price": "€75,000",
            "caracteristicasTecnicas": [
                {"clave": "Potencia", "valor": "200 HP"},
                {"clave": "Transmisión", "valor": "Automática Powershift"},
            ],
            "argumentosDeVenta": {
                "propuestaUnicaDeValor": "El equilibrio perfecto entre potencia, tecnología y confort para el agricultor moderno.",
                "beneficiosPrincipales": ["Ahorro de combustible del 15%", "Mayor productividad por hectárea", "Mantenimiento reducido"],
            }
        }
    return json.dumps(details)

# --- Agente Principal del Embudo ---
# Este agente es el "cerebro". Decide qué hacer en cada paso del embudo.
# Su instrucción es clave para que devuelva JSON estructurado.

funnel_agent = LlmAgent(
    name="FunnelAgent",
    model=GEMINI_MODEL,
    instruction= INSTRUCTION,
    tools=[
        herramientas_produccion_agroasesoria.ask_contact_name_tool,
        herramientas_produccion_agroasesoria.get_or_create_user_profile_from_firestore_tool,
        herramientas_produccion_agroasesoria.update_user_profile_in_firestore_tool,
        herramientas_produccion_agroasesoria.determine_next_profile_question_tool,
        herramientas_produccion_agroasesoria.get_catalog_level_options_tool,
        herramientas_produccion_agroasesoria.get_products_final_list_tool,
        herramientas_produccion_agroasesoria.get_detailed_product_info_tool,
        herramientas_produccion_agroasesoria.get_current_datetime_tool,
        herramientas_produccion_agroasesoria.ask_pain_points_questions_tool,
        herramientas_produccion_agroasesoria.search_internal_products_by_embedding_tool,
        herramientas_produccion_agroasesoria.search_external_products_tool,
        herramientas_produccion_agroasesoria.add_to_products_a_repasar_in_firestore_tool,
        herramientas_produccion_agroasesoria.request_video_upload_link_tool,
        herramientas_produccion_agroasesoria.prepare_selection_update_for_session_state,
        herramientas_produccion_agroasesoria.get_alternative_products_tool,
    ]
)

# Para ADK, el agente raíz debe llamarse `root_agent` si usas `adk run` o `adk web`.
# Para ejecución programática como en este script, el nombre no es restrictivo.
# Aquí, FunnelAgent es nuestro agente principal.
root_agent = funnel_agent


# --- Función principal para ejecutar el agente (simulación) ---
async def run_conversation():
    print("Inicializando servicio de sesión en memoria...")
    session_service = InMemorySessionService()

    print(f"Creando Runner para la app: {APP_NAME}...")
    # Nota: El Runner en ADK gestiona la ejecución del agente.
    # Aquí no se especifican PROJECT_ID, LOCATION, AGENT_ENGINE_ID
    # porque InMemorySessionService no los necesita.
    # Si usaras VertexAiSessionService, sí serían necesarios para ese servicio.
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
        # No se necesita `model` aquí si ya está definido en el LlmAgent
    )

    # Crear una nueva sesión o resumir una existente
    session_id = f"{SESSION_ID_BASE}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    print(f"Creando nueva sesión: {session_id} para el usuario: {USER_ID}")

    # Estado inicial del embudo
    current_session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
        state=initial_state
    )
    print(f"Estado inicial de la sesión: {current_session.state}")
    current_session.state[STATE_FUNNEL_STEP] = "WELCOME"
    print(f"Estado inicial de la sesión: {current_session.state}")

    # Simular una conversación
    user_inputs = [
        "Hola, estoy buscando maquinaria.",
        "Me interesan los tractores. ID: cat_tractors", # Usuario selecciona categoría
        "Quiero más detalles del SuperTractor X1000. ID: prod_trac_001", # Usuario selecciona producto
        "Gracias, eso es todo por ahora."
    ]

    for user_text in user_inputs:
        print(f"\n>>> Usuario: {user_text}")

        # El mensaje del usuario debe estar en formato Content
        user_content = genai_types.Content(parts=[genai_types.Part(text=user_text)])

        # Ejecutar el agente
        # El runner.run() devuelve un generador de eventos.
        # Necesitamos iterar para obtener la respuesta final del agente.
        final_agent_response_json_str = None
        async for event in runner.run_async(
            session_id=current_session.id,
            user_id=USER_ID, # ADK Runner espera user_id aquí también
            new_message=user_content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                # Asumimos que la instrucción al LLM de devolver JSON se ha cumplido.
                final_agent_response_json_str = event.content.parts[0].text
                break
            # Aquí podrías manejar otros tipos de eventos si es necesario (tool calls, etc.)
            # print(f"    Evento intermedio: {event.type}, Autor: {event.author}")

        if final_agent_response_json_str:
            print(f" Respuesta Estructurada del Agente:\n{final_agent_response_json_str}")
            try:
                structured_response = json.loads(final_agent_response_json_str)
                # Actualizar el estado del embudo en la sesión para el próximo turno
                # La instrucción del LLM le indica que sugiera el "next_funnel_step".
                # La aplicación (este script en este caso) es responsable de actualizar el session.state.
                # Una alternativa más avanzada es que el LLM use una herramienta para actualizar el estado.
                if "next_funnel_step" in structured_response:
                    new_funnel_step = structured_response.get("next_funnel_step")
                    # También podrías querer guardar otros datos que el LLM haya procesado
                    # Por ejemplo, si el LLM identifica un selected_category_id de la entrada del usuario
                    # antes de llamar al tool, podría devolverlo en el JSON para que lo guardes aquí.
                    # Para simplificar, asumimos que la instrucción del LLM es lo suficientemente buena
                    # como para usar los tools correctamente y que los IDs se manejan internamente por ahora.

                    # Para una lógica más robusta, el LLM podría devolver los IDs seleccionados
                    # y aquí actualizaríamos session.state.{STATE_SELECTED_CATEGORY}, etc.
                    # Por ejemplo:

                    if "selected_category_id" in structured_response.get("data", {}):
                      current_session.state[STATE_SELECTED_CATEGORY] = structured_response["data"]["selected_category_id"]

                    if new_funnel_step:
                        print(f"  Actualizando estado del embudo a: {new_funnel_step}")
                        current_session.state[STATE_FUNNEL_STEP] = new_funnel_step
                        # Guardar el cambio de estado en el session_service
                        # Esto se hace implícitamente cuando el runner procesa el evento
                        # que causó la respuesta final, si ese evento tuviera un state_delta.
                        # Como aquí actualizamos el estado *después* de la respuesta del LLM,
                        # necesitaríamos una forma de persistir este cambio si el script terminara.
                        # En una app real con múltiples request/response, el estado se cargaría
                        # y guardaría en cada interacción a través del session_service.
                        # Por ahora, la sesión en memoria se actualiza directamente.
                print(f"  Estado actual de la sesión: {current_session.state}")


            except json.JSONDecodeError:
                print("Error: La respuesta del agente no es un JSON válido.")
        else:
            print("El agente no devolvió una respuesta final estructurada.")

    print("\nFin de la conversación.")

# if __name__ == "__main__":
#    import asyncio
#    # Para ejecutar código async en un script
#    # Si usas Jupyter Notebook, puedes usar `await run_conversation()` directamente en una celda
#    # después de configurar el bucle de eventos de asyncio si es necesario.
#    asyncio.run(run_conversation())