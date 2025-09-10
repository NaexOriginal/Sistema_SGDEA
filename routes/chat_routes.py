from flask import Blueprint, jsonify, request
from shared.document_context import get_documento_contexto
from ai_modules.ai_chat_handler import responder_chat

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    documento_contexto = get_documento_contexto()
    
    try:
        # Verificar si hay un documento disponible
        if not documento_contexto["disponible"]:
            return jsonify({
                "status": "error",
                "message": "No hay ningún documento procesado. Por favor, procesa un documento primero."
            })
        
        # Obtener la pregunta del usuario
        data = request.get_json()
        pregunta = data.get('pregunta', '').strip()
        pagina_especifica = data.get('pagina', None)
        
        if not pregunta:
            return jsonify({
                "status": "error",
                "message": "Por favor, proporciona una pregunta."
            })
        
        # Usar OpenAI para responder basándose en el contexto del documento
        contexto = documento_contexto["texto"]
        
        # Si se especifica una página, filtrar el contexto
        if pagina_especifica:
            try:
                pagina_num = int(pagina_especifica)
                if pagina_num in documento_contexto["paginas"]:
                    contenido_pagina = documento_contexto["paginas"][pagina_num]
                    contexto = f"=== PÁGINA {pagina_num} ===\n--- Página {pagina_num} (Seleccionada) ---\n{contenido_pagina}\n--- Fin Página {pagina_num} ---"
                else:
                    return jsonify({
                        "status": "error",
                        "message": f"La página {pagina_num} no existe en el documento. Páginas disponibles: {list(documento_contexto['paginas'].keys())}"
                    })
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "El número de página debe ser un entero válido."
                })
        
        respuesta = responder_chat(pregunta, contexto)
        
        return jsonify({
            "status": "success",
            "pregunta": pregunta,
            "respuesta": respuesta,
            "pagina_usada": pagina_especifica if pagina_especifica else "auto-seleccionada"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al procesar la pregunta: {str(e)}"
        })