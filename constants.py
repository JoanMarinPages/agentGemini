# IMPORTANTE: No hardcodees API keys en el código
# Usa variables de entorno o archivos de configuración
GOOGLE_API_KEY = None  # Configurar desde .env
GOOGLE_GENAI_USE_VERTEXAI = False

APP_NAME = "sales_funnel_app"
USER_ID = "dev_user_01"
SESSION_ID_BASE = "funnel_session"
GEMINI_MODEL = "gemini-2.0-flash"
STATE_INITIAL_TOPIC = "initial_topic"

STATE_CURRENT_DOC = "current_document"
STATE_FUNEL = "criticism"
COMPLETION_PHRASE = "No major issues found."


# --- Estado del Embudo (claves para session.state) ---
STATE_FUNNEL_STEP = "funnel_step"
STATE_SELECTED_TYPE_STATE = "selected_typestate_id"
STATE_SELECTED_STATE = "selected_state_id"
STATE_SELECTED_CATEGORY = "selected_category_id"
STATE_SELECTED_SUB_CATEGORY = "selected_sub_category_id"
STATE_SELECTED_SUB_SUB_CATEGORY = "selected_sub_sub_category_id"
STATE_SELECTED_PRODUCT_TYPE = "selected_product_type_id"
STATE_SELECTED_PRODUCT = "selected_product_id"