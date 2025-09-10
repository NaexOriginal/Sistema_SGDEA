from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from get_documents import analizar_archivo_completo
from openai_classifier import clasificarcion_openai, extraer_paginas_del_contexto, clasificacion_por_paginas
from spacy_nlp import extraer_entidades
from shared.document_context import get_documento_contexto, set_documento_contexto
import datetime
import os
import json

document_bp = Blueprint('document', __name__)

@document_bp.route('/procesar_formulario', methods=['POST'])
def procesar_formulario():
    
    # 1. Obtenemos la información del formulario
    asunto = request.form.get('asunto', '')
    cuerpo_mensaje = request.form.get('cuerpo_mensaje', '')
    
    # 2. Manejar los archivos adjuntos
    adjuntos_texto = ""
    adjuntos_detectados = []
    analisis_archivos = []
    
    if 'archivo' in request.files:
        archivos = request.files.getlist('archivo')
        for archivo in archivos:
            if archivo.filename != '':
                # Usar secure_filename para evitar problemas de seguridad
                filename = secure_filename(archivo.filename)
                filepath = os.path.join('uploads', filename)
                archivo.save(filepath)
                
                # Leer el archivo y procesarlo con la función
                with open(filepath, 'rb') as f:
                    file_data = f.read()
                    
                # Análisis completo del archivo
                analisis_completo = analizar_archivo_completo(filename, file_data)
                analisis_archivos.append(analisis_completo)
                
                adjuntos_detectados.append(filename)
                adjuntos_texto += analisis_completo["texto_extraido"]
                
                # Opcional: Eliminar el archivo después de procesarlo
                os.remove(filepath)
                
    # 3. Combinar todo el texto para el procesamiento NLP
    texto_total = cuerpo_mensaje + "\n\n" + adjuntos_texto
    
    # Aquí puedes llamar a tu función de NLP para extraer la información
    info_clave = extraer_entidades(texto_total)
    
    # Paso extra: Usar OpenAI para la clasificación de archivos
    clasificacion_documental = clasificarcion_openai(texto_total)
    
    # Extraer páginas separadas del texto
    paginas_separadas = extraer_paginas_del_contexto(texto_total)
    
    # Clasificar cada página individualmente
    clasificaciones_por_pagina = clasificacion_por_paginas(paginas_separadas)

    # 4. Crear el contexto completo para guardar
    contexto_completo = {
        "timestamp": datetime.datetime.now().isoformat(),
        "asunto": asunto,
        "cuerpo_mensaje": cuerpo_mensaje,
        "adjuntos_detectados": adjuntos_detectados,
        "analisis_archivos": analisis_archivos,
        "texto_extraido": texto_total,
        "informacion_clave": info_clave,
        "clasificacion_documental_openai": clasificacion_documental,
        "clasificaciones_por_pagina": clasificaciones_por_pagina,
        "total_paginas": len(paginas_separadas)
    }
    
    # 5. Guardar el contexto en un archivo JSON
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"contexto_{timestamp_str}.json"
    ruta_archivo = os.path.join("contextos_guardados", nombre_archivo)
    
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump(contexto_completo, f, ensure_ascii=False, indent=2)
    
    # 6. Guardar el contexto del documento para el chat
    nuevo_contexto = {
        "texto": texto_total,
        "analisis": analisis_archivos,
        "paginas": paginas_separadas,
        "clasificaciones_paginas": clasificaciones_por_pagina,
        "total_paginas": len(paginas_separadas),
        "disponible": True
    }
    set_documento_contexto(nuevo_contexto)
    
    # 7. Devolver una respuesta JSON con el resultado
    return jsonify({
        "status": "success",
        "archivo_contexto": nombre_archivo,
        "ruta_contexto": ruta_archivo,
        "cuerpo": cuerpo_mensaje,
        "adjuntos_detectados": adjuntos_detectados,
        "analisis_archivos": analisis_archivos,
        "texto_extraido": texto_total,
        "informacion_clave": info_clave,
        "clasifiacion_documental_openai": clasificacion_documental,
        "clasificaciones_por_pagina": clasificaciones_por_pagina,
        "total_paginas": len(paginas_separadas)
    })

@document_bp.route('/listar_paginas', methods=['GET'])
def listar_paginas():
    """Endpoint para listar las páginas disponibles en el documento"""
    documento_contexto = get_documento_contexto()
    
    try:
        if not documento_contexto["disponible"]:
            return jsonify({
                "status": "error",
                "message": "No hay ningún documento procesado."
            })
        
        # Usar la estructura de páginas ya extraída
        paginas_info = []
        for num_pagina, contenido in documento_contexto["paginas"].items():
            # Crear un resumen corto de cada página
            resumen = contenido[:100] + "..." if len(contenido) > 100 else contenido
            
            # Agregar información de clasificación si está disponible
            info_pagina = {
                "numero": num_pagina,
                "resumen": resumen,
                "clasificacion": None
            }
            
            # Si hay clasificaciones disponibles, incluirlas
            if "clasificaciones_paginas" in documento_contexto and num_pagina in documento_contexto["clasificaciones_paginas"]:
                clasificacion = documento_contexto["clasificaciones_paginas"][num_pagina]
                if "error" not in clasificacion:
                    info_pagina["clasificacion"] = {
                        "asunto": clasificacion.get("asunto", "Sin clasificar"),
                        "serie_documental": clasificacion.get("serie_documental", "Sin clasificar"),
                        "contenido_relevante": clasificacion.get("contenido_relevante", "Sin determinar")
                    }
                else:
                    info_pagina["clasificacion"] = {"error": clasificacion["error"]}
            
            paginas_info.append(info_pagina)
        
        return jsonify({
            "status": "success",
            "total_paginas": documento_contexto["total_paginas"],
            "paginas": paginas_info
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al listar páginas: {str(e)}"
        })

@document_bp.route('/clasificaciones_paginas', methods=['GET'])
def obtener_clasificaciones_paginas():
    """Endpoint para obtener las clasificaciones detalladas por páginas"""
    documento_contexto = get_documento_contexto()
    
    try:
        if not documento_contexto["disponible"]:
            return jsonify({
                "status": "error",
                "message": "No hay ningún documento procesado."
            })
        
        if "clasificaciones_paginas" not in documento_contexto:
            return jsonify({
                "status": "error",
                "message": "No hay clasificaciones por páginas disponibles. El documento debe ser reprocesado."
            })
        
        return jsonify({
            "status": "success",
            "total_paginas": documento_contexto["total_paginas"],
            "clasificaciones": documento_contexto["clasificaciones_paginas"]
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al obtener clasificaciones: {str(e)}"
        })

@document_bp.route('/clasificacion_pagina/<int:numero_pagina>', methods=['GET'])
def obtener_clasificacion_pagina_especifica(numero_pagina):
    """Endpoint para obtener la clasificación de una página específica"""
    documento_contexto = get_documento_contexto()
    
    try:
        if not documento_contexto["disponible"]:
            return jsonify({
                "status": "error",
                "message": "No hay ningún documento procesado."
            })
        
        if numero_pagina not in documento_contexto["paginas"]:
            return jsonify({
                "status": "error",
                "message": f"La página {numero_pagina} no existe. Páginas disponibles: {list(documento_contexto['paginas'].keys())}"
            })
        
        if "clasificaciones_paginas" not in documento_contexto or numero_pagina not in documento_contexto["clasificaciones_paginas"]:
            return jsonify({
                "status": "error",
                "message": f"No hay clasificación disponible para la página {numero_pagina}."
            })
        
        clasificacion = documento_contexto["clasificaciones_paginas"][numero_pagina]
        contenido_pagina = documento_contexto["paginas"][numero_pagina]
        
        return jsonify({
            "status": "success",
            "numero_pagina": numero_pagina,
            "contenido": contenido_pagina,
            "clasificacion": clasificacion
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al obtener clasificación de página: {str(e)}"
        })

# La función get_documento_contexto ahora se importa desde shared.document_context