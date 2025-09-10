import os
from services.pdf_service import extraer_texto_pdf, detectar_tipo_pdf
from services.image_service import extraer_texto_imagen, es_formato_imagen_soportado
from services.document_service import extraer_texto_docx, es_formato_docx

def extraer_texto_archivo(filename, file_data):
    """
    Extrae texto de un archivo usando el servicio apropiado según su extensión.
    
    Args:
        filename (str): Nombre del archivo
        file_data (bytes): Datos binarios del archivo
        
    Returns:
        str: Texto extraído del archivo
    """
    texto_extraido = ""
    extension = os.path.splitext(filename)[1].lower()
    
    if extension == ".pdf":
        texto_extraido = extraer_texto_pdf(file_data)
        
    elif es_formato_docx(extension):
        texto_extraido = extraer_texto_docx(file_data)
        
    elif es_formato_imagen_soportado(extension):
        texto_extraido = extraer_texto_imagen(file_data)
        
    else:
        pass
        
    return texto_extraido

def analizar_archivo_completo(filename, file_data):
    """
    Analiza un archivo y proporciona información detallada sobre su contenido.
    
    Args:
        filename (str): Nombre del archivo
        file_data (bytes): Datos binarios del archivo
        
    Returns:
        dict: Información completa del archivo incluyendo texto y metadatos
    """
    extension = os.path.splitext(filename)[1].lower()
    resultado = {
        "filename": filename,
        "extension": extension,
        "texto_extraido": "",
        "metadatos": {}
    }
    
    if extension == ".pdf":
        # Para PDFs, obtener tanto el texto como información del tipo
        resultado["texto_extraido"] = extraer_texto_pdf(file_data)
        resultado["metadatos"] = detectar_tipo_pdf(file_data)
        
    elif es_formato_docx(extension):
        resultado["texto_extraido"] = extraer_texto_docx(file_data)
        resultado["metadatos"] = {"tipo": "documento_word"}
        
    elif es_formato_imagen_soportado(extension):
        resultado["texto_extraido"] = extraer_texto_imagen(file_data)
        resultado["metadatos"] = {"tipo": "imagen_ocr"}
        
    else:
        resultado["metadatos"] = {"error": "Formato no soportado"}
        
    return resultado