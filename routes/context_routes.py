from flask import Blueprint, jsonify, request
import os
import json
from shared.document_context import get_documento_contexto, set_documento_contexto

context_bp = Blueprint('context', __name__)

@context_bp.route('/cargar_contexto', methods=['POST'])
def cargar_contexto():
    """Cargar contexto desde un archivo JSON subido o seleccionado"""

    
    try:
        # Opción 1: Archivo JSON subido
        if 'archivo_json' in request.files:
            archivo = request.files['archivo_json']
            if archivo.filename != '' and archivo.filename.endswith('.json'):
                contenido = archivo.read().decode('utf-8')
                contexto_data = json.loads(contenido)
                
                # Actualizar el contexto global
                nuevo_contexto = {
                    "texto": contexto_data.get("texto_extraido", ""),
                    "analisis": contexto_data.get("analisis_archivos", []),
                    "disponible": True
                }
                set_documento_contexto(nuevo_contexto)
                
                return jsonify({
                    "status": "success",
                    "mensaje": "Contexto cargado desde archivo JSON",
                    "contexto_info": {
                        "timestamp": contexto_data.get("timestamp", ""),
                        "asunto": contexto_data.get("asunto", ""),
                        "adjuntos": contexto_data.get("adjuntos_detectados", [])
                    }
                })
        
        # Opción 2: Seleccionar archivo existente por nombre
        elif 'nombre_archivo' in request.json:
            nombre_archivo = request.json['nombre_archivo']
            ruta_archivo = os.path.join("contextos_guardados", nombre_archivo)
            
            if os.path.exists(ruta_archivo):
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    contexto_data = json.load(f)
                
                # Actualizar el contexto global
                nuevo_contexto = {
                    "texto": contexto_data.get("texto_extraido", ""),
                    "analisis": contexto_data.get("analisis_archivos", []),
                    "disponible": True
                }
                set_documento_contexto(nuevo_contexto)
                
                return jsonify({
                    "status": "success",
                    "mensaje": "Contexto cargado desde archivo guardado",
                    "contexto_info": {
                        "timestamp": contexto_data.get("timestamp", ""),
                        "asunto": contexto_data.get("asunto", ""),
                        "adjuntos": contexto_data.get("adjuntos_detectados", [])
                    }
                })
            else:
                return jsonify({"status": "error", "mensaje": "Archivo no encontrado"})
        
        else:
            return jsonify({"status": "error", "mensaje": "No se proporcionó archivo JSON o nombre de archivo"})
            
    except Exception as e:
        return jsonify({"status": "error", "mensaje": f"Error al cargar contexto: {str(e)}"})

@context_bp.route('/listar_contextos', methods=['GET'])
def listar_contextos():
    """Listar todos los archivos de contexto disponibles"""
    try:
        contextos = []
        if os.path.exists("contextos_guardados"):
            for archivo in os.listdir("contextos_guardados"):
                if archivo.endswith('.json'):
                    ruta_completa = os.path.join("contextos_guardados", archivo)
                    try:
                        with open(ruta_completa, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        contextos.append({
                            "nombre_archivo": archivo,
                            "timestamp": data.get("timestamp", ""),
                            "asunto": data.get("asunto", "Sin asunto"),
                            "adjuntos": len(data.get("adjuntos_detectados", [])),
                            "tamaño_kb": round(os.path.getsize(ruta_completa) / 1024, 2)
                        })
                    except:
                        # Si hay error leyendo el archivo, incluirlo con info básica
                        contextos.append({
                            "nombre_archivo": archivo,
                            "timestamp": "Error al leer",
                            "asunto": "Error al leer archivo",
                            "adjuntos": 0,
                            "tamaño_kb": round(os.path.getsize(ruta_completa) / 1024, 2)
                        })
        
        return jsonify({
            "status": "success",
            "contextos": sorted(contextos, key=lambda x: x["timestamp"], reverse=True)
        })
        
    except Exception as e:
        return jsonify({"status": "error", "mensaje": f"Error al listar contextos: {str(e)}"})