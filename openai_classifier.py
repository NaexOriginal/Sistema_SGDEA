# Archivo principal que importa y expone las funciones de IA
# Este archivo actúa como un punto de entrada único para las funcionalidades de IA

from ai_modules.ai_document_classifier import clasificarcion_openai, clasificacion_por_paginas
from ai_modules.ai_chat_handler import responder_chat, extraer_paginas_del_contexto, listar_paginas_disponibles

# Exportar las funciones para mantener compatibilidad con el resto del sistema
__all__ = ['clasificarcion_openai', 'clasificacion_por_paginas', 'responder_chat', 'extraer_paginas_del_contexto', 'listar_paginas_disponibles']