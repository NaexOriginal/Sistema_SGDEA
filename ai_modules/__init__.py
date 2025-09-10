# Módulo de IA para el Sistema SGDEA
# Contiene funciones para clasificación documental y chat conversacional

from .ai_document_classifier import clasificarcion_openai, clasificacion_por_paginas
from .ai_chat_handler import responder_chat, extraer_paginas_del_contexto, listar_paginas_disponibles

__all__ = ['clasificarcion_openai', 'clasificacion_por_paginas', 'responder_chat', 'extraer_paginas_del_contexto', 'listar_paginas_disponibles']