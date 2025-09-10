import os
from services.pdf_service import extraer_texto_pdf
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
        print(f"Formato de archivo no soportado: {extension}")
        
    return texto_extraido